#!/usr/bin/env python
"""CARR-lite v2: abundance correction plus a soft rare-cell presence branch.

This module imports the validated v1 data/metric code.  Biological base
scenarios, including all sequencing depths, are kept wholly out of training.
The presence branch never uses held-out labels or held-out calibration.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import carr_lite_tangram as v1


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-root", required=True)
    p.add_argument("--prediction-root", required=True)
    p.add_argument("--bases", nargs="+",
                   default=["B01_stable_bg3", "B08_confusable_bg3"])
    p.add_argument("--out-dir", default="carr_lite_v2_results")
    p.add_argument("--confusion-k", type=int, default=3)
    p.add_argument("--marker-k", type=int, default=40)
    p.add_argument("--seed", type=int, default=20260724)
    p.add_argument("--gate-strengths", nargs="+", type=float,
                   default=[0.15, 0.30, 0.50])
    return p.parse_args()


def target_truth(dataset):
    values = []
    for spot_id in dataset["truth"].index:
        target = str(dataset["metadata"].at[spot_id, "target_cell_type"])
        values.append(float(dataset["truth"].at[spot_id, target]))
    return np.asarray(values)


def set_local_target(dataset, target_values):
    """Move mass only inside each target/confusion set to reach target_values."""
    current = np.asarray([
        dataset["prediction"].at[s, str(dataset["metadata"].at[s, "target_cell_type"])]
        for s in dataset["prediction"].index
    ])
    return v1.apply_local_correction(dataset, np.asarray(target_values) - current)


def soft_presence_fusion(dataset, abundance_prediction, presence_probability,
                         positive_prediction, strength):
    """Blend quantitative abundance with the expected positive abundance.

    Presence probability supplies ranking evidence; the positive-abundance
    model supplies scale.  A bounded blend prevents the classifier from
    replacing the validated quantitative correction outright.
    """
    expected = np.clip(presence_probability, 0.0, 1.0) * np.maximum(
        positive_prediction, 0.0
    )
    desired = (1.0 - strength) * abundance_prediction + strength * expected
    local_cap = []
    for i, spot_id in enumerate(dataset["prediction"].index):
        target = str(dataset["metadata"].at[spot_id, "target_cell_type"])
        d = dataset["definitions"][target]
        local_cap.append(
            dataset["prediction"].iloc[i, d["target_index"]] +
            dataset["prediction"].iloc[i, d["confusion_indices"]].sum()
        )
    return np.clip(desired, 0.0, np.asarray(local_cap))


def balanced_weights(y):
    y = np.asarray(y, dtype=int)
    n0, n1 = max(np.sum(y == 0), 1), max(np.sum(y == 1), 1)
    return np.where(y == 1, len(y) / (2.0 * n1), len(y) / (2.0 * n0))


def main():
    args = parse_args()
    data_root, pred_root = Path(args.data_root), Path(args.prediction_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    datasets = []
    for base in args.bases:
        for depth in v1.DEPTHS:
            print(f"Loading {base}, depth={depth}", flush=True)
            datasets.append(v1.build_dataset(
                base, depth, data_root, pred_root,
                args.confusion_k, args.marker_k
            ))

    metric_rows = []
    prediction_manifest = []
    for held_out in args.bases:
        train = [d for d in datasets if d["base"] != held_out]
        test = [d for d in datasets if d["base"] == held_out]
        x_train = pd.concat([d["features"] for d in train]).to_numpy()
        truth_train = np.concatenate([target_truth(d) for d in train])
        delta_train = np.concatenate([d["labels"].to_numpy() for d in train])
        presence_train = (truth_train > 0).astype(int)

        abundance_model = HistGradientBoostingRegressor(
            learning_rate=0.05, max_iter=250, max_leaf_nodes=15,
            l2_regularization=1.0, random_state=args.seed,
        )
        abundance_model.fit(x_train, delta_train)

        positive_model = HistGradientBoostingRegressor(
            learning_rate=0.04, max_iter=200, max_leaf_nodes=10,
            l2_regularization=2.0, random_state=args.seed + 1,
        )
        positive_mask = presence_train == 1
        positive_model.fit(x_train[positive_mask], truth_train[positive_mask])

        classifiers = {
            "Logit": make_pipeline(
                StandardScaler(),
                LogisticRegression(
                    C=0.3, class_weight="balanced", max_iter=2000,
                    random_state=args.seed,
                ),
            ),
            "HGBC": HistGradientBoostingClassifier(
                learning_rate=0.04, max_iter=200, max_leaf_nodes=10,
                l2_regularization=2.0, random_state=args.seed,
            ),
        }
        classifiers["Logit"].fit(x_train, presence_train)
        classifiers["HGBC"].fit(
            x_train, presence_train, sample_weight=balanced_weights(presence_train)
        )

        fold_dir = out_dir / f"held_out_{held_out}"
        fold_dir.mkdir(exist_ok=True)
        for d in test:
            seed = args.seed + int(d["depth"])
            metric_rows.append(v1.evaluate(d, d["prediction"], "Tangram", seed))

            x_test = d["features"].to_numpy()
            delta = abundance_model.predict(x_test)
            quantitative = v1.apply_local_correction(d, delta)
            q_target = np.asarray([
                quantitative.at[s, str(d["metadata"].at[s, "target_cell_type"])]
                for s in quantitative.index
            ])
            metric_rows.append(v1.evaluate(
                d, quantitative, "V2_AbundanceOnly", seed
            ))
            quantitative.to_csv(
                fold_dir / f"V2_AbundanceOnly_{d['depth']}.csv"
            )

            positive = positive_model.predict(x_test)
            for clf_name, classifier in classifiers.items():
                probability = classifier.predict_proba(x_test)[:, 1]
                for strength in args.gate_strengths:
                    desired = soft_presence_fusion(
                        d, q_target, probability, positive, strength
                    )
                    corrected = set_local_target(d, desired)
                    method = f"V2_{clf_name}_Gate_a{int(round(strength * 100)):02d}"
                    corrected.to_csv(fold_dir / f"{method}_{d['depth']}.csv")
                    metric_rows.append(v1.evaluate(d, corrected, method, seed))
                    prediction_manifest.append({
                        "held_out_base": held_out,
                        "depth": d["depth"],
                        "method": method,
                        "gate_strength": strength,
                        "presence_probability_mean": float(probability.mean()),
                        "desired_target_mean": float(desired.mean()),
                    })

    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(out_dir / "carr_lite_v2_metrics_by_fold.csv", index=False)
    summary = metrics.groupby(["held_out_base", "method"], as_index=False).agg(
        n_depths=("depth", "count"),
        matrix_RMSE_mean=("matrix_RMSE", "mean"),
        target_RMSE_mean=("target_RMSE", "mean"),
        target_MAE_mean=("target_MAE", "mean"),
        balanced_AUPRC_mean=("balanced_AUPRC", "mean"),
        recall_at_10pct_FPR_mean=("recall_at_10pct_FPR", "mean"),
    )
    summary.to_csv(out_dir / "carr_lite_v2_summary.csv", index=False)
    pd.DataFrame(prediction_manifest).to_csv(
        out_dir / "presence_gate_manifest.csv", index=False
    )
    with open(out_dir / "run_config.json", "w", encoding="utf-8") as f:
        json.dump(vars(args), f, ensure_ascii=False, indent=2)
    print("\n" + summary.to_string(index=False), flush=True)
    print(f"\nResults written to: {out_dir.resolve()}", flush=True)


if __name__ == "__main__":
    main()
