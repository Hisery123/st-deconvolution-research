#!/usr/bin/env python
"""Strict 13-fold CARR-lite V2 validation on the 52-scenario rare-cell suite.

Each biological base scenario (all four sequencing depths) is held out as one
fold. Models are trained on the other base scenarios only. Existing Tangram
predictions are corrected and written into each view's predictions directory.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

import carr_lite_tangram as v1
import carr_lite_tangram_v2 as v2


DEFAULT_SUITE = r"D:\Research\STdeconv_benchmark\data\groundtruth\rarecell_52scenario_suite"
DEFAULT_EVALUATOR = (
    r"D:\Research\STdeconv_benchmark\evaluation & visualization"
    r"\evaluate_rarecell_predictions.py"
)
METHOD_FILES = {
    "CARRliteV2_AbundanceOnly": "CARRliteV2_AbundanceOnly.csv",
    "CARRliteV2_HGBC_a15": "CARRliteV2_HGBC_a15.csv",
    "CARRliteV2_HGBC_a30": "CARRliteV2_HGBC_a30.csv",
    "CARRliteV2_HGBC_a50": "CARRliteV2_HGBC_a50.csv",
}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--suite_root", default=DEFAULT_SUITE)
    p.add_argument("--evaluator", default=DEFAULT_EVALUATOR)
    p.add_argument("--python", default=sys.executable)
    p.add_argument("--confusion_k", type=int, default=3)
    p.add_argument("--marker_k", type=int, default=40)
    p.add_argument("--seed", type=int, default=20260724)
    p.add_argument("--force", action="store_true")
    p.add_argument("--skip_evaluation", action="store_true")
    p.add_argument("--fail_fast", action="store_true")
    return p.parse_args()


def read_manifest(path):
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def base_from_scenario(scenario_id):
    if "_depth_" not in scenario_id:
        raise ValueError("scenario_id lacks '_depth_': {}".format(scenario_id))
    return scenario_id.rsplit("_depth_", 1)[0]


def depth_from_scenario(scenario_id):
    return scenario_id.rsplit("_depth_", 1)[1]


def resolve_view_dir(suite_root, row):
    candidate = Path(row.get("view_dir", ""))
    if candidate.is_dir():
        return candidate
    fallback = suite_root / "scenario_views" / row["scenario_id"]
    if fallback.is_dir():
        return fallback
    raise FileNotFoundError("View directory not found for {}".format(row["scenario_id"]))


def read_indexed(path):
    frame = pd.read_csv(path, index_col=0, low_memory=False)
    frame.index = frame.index.astype(str)
    frame.columns = frame.columns.astype(str)
    return frame


def find_expression(view_dir):
    direct = view_dir / "pseudo_spot_expression.csv"
    if direct.is_file():
        return direct
    matches = sorted(view_dir.glob("pseudo_spot_expression_depth_*.csv"))
    if len(matches) == 1:
        return matches[0]
    raise FileNotFoundError("Cannot find one pseudo-spot expression file in {}".format(view_dir))


def build_view_dataset(view_dir, scenario_id, confusion_k, marker_k):
    truth = read_indexed(view_dir / "pseudo_spot_ground_truth.csv")
    metadata = read_indexed(view_dir / "spot_metadata.csv")
    prediction = read_indexed(
        view_dir / "predictions" / "Tangram_self_benchmark.csv"
    )
    expression = read_indexed(find_expression(view_dir))

    prediction = prediction.loc[truth.index, truth.columns]
    expression = expression.loc[truth.index]
    metadata = metadata.loc[truth.index]
    prediction.iloc[:, :] = v1.normalize_rows(prediction.to_numpy())

    profiles = v1.reference_profiles(view_dir, expression.columns, truth.columns)
    targets = metadata["target_cell_type"].astype(str).drop_duplicates().tolist()
    definitions, log_profiles = v1.build_type_definitions(
        profiles, targets, confusion_k, marker_k
    )

    observed_log = np.log1p(v1.normalize_rows(expression.to_numpy()) * 1e6)
    pred_arr = prediction.to_numpy()
    reconstructed_log = np.log1p(
        np.maximum(pred_arr @ profiles.to_numpy(), 0.0) * 1e6
    )
    rows, labels = [], []
    for row_i, spot_id in enumerate(truth.index):
        target = str(metadata.at[spot_id, "target_cell_type"])
        d = definitions[target]
        ti, ci, mi = d["target_index"], d["confusion_indices"], d["marker_indices"]
        base_target = pred_arr[row_i, ti]
        conf_values = pred_arr[row_i, ci]
        obs_marker = observed_log[row_i, mi].mean()
        target_marker_ref = log_profiles[ti, mi].mean()
        conf_marker_ref = log_profiles[ci][:, mi].mean()
        residual = observed_log[row_i] - reconstructed_log[row_i]
        direction = d["contrast"]
        rows.append({
            "base_target": base_target,
            "base_confusion_sum": conf_values.sum(),
            "base_target_minus_confmax": base_target - conf_values.max(),
            "base_target_share_local": base_target / max(
                base_target + conf_values.sum(), v1.EPS
            ),
            "observed_marker_score": obs_marker,
            "observed_marker_margin": obs_marker - conf_marker_ref,
            "marker_fit_target": -abs(obs_marker - target_marker_ref),
            "residual_projection": float(
                residual @ direction / max(np.linalg.norm(direction), v1.EPS)
            ),
            "residual_marker_mean": float(residual[mi].mean()),
            "library_size_log": float(np.log1p(expression.iloc[row_i].sum())),
            "reference_similarity_max": d["reference_similarity_max"],
            "depth_fraction": int(depth_from_scenario(scenario_id)) / 100.0,
        })
        labels.append(float(truth.iloc[row_i, ti] - base_target))

    return {
        "base": base_from_scenario(scenario_id),
        "depth": depth_from_scenario(scenario_id),
        "scenario_id": scenario_id,
        "view_dir": view_dir,
        "truth": truth,
        "metadata": metadata,
        "prediction": prediction,
        "features": pd.DataFrame(rows, index=truth.index),
        "labels": pd.Series(labels, index=truth.index, name="delta"),
        "definitions": definitions,
    }


def valid_prediction(path, truth):
    if not path.is_file():
        return False
    try:
        pred = read_indexed(path)
        return (
            pred.shape == truth.shape
            and set(pred.index) == set(truth.index)
            and set(pred.columns) == set(truth.columns)
            and np.isfinite(pred.to_numpy()).all()
            and (pred.to_numpy() >= -1e-9).all()
            and np.allclose(pred.sum(axis=1), 1.0, atol=1e-5)
        )
    except Exception:
        return False


def train_fold(train, seed):
    x = pd.concat([d["features"] for d in train]).to_numpy()
    delta = np.concatenate([d["labels"].to_numpy() for d in train])
    truth = np.concatenate([v2.target_truth(d) for d in train])
    presence = (truth > 0).astype(int)

    abundance = HistGradientBoostingRegressor(
        learning_rate=0.05, max_iter=250, max_leaf_nodes=15,
        l2_regularization=1.0, random_state=seed,
    ).fit(x, delta)
    positive = HistGradientBoostingRegressor(
        learning_rate=0.04, max_iter=200, max_leaf_nodes=10,
        l2_regularization=2.0, random_state=seed + 1,
    ).fit(x[presence == 1], truth[presence == 1])
    classifier = HistGradientBoostingClassifier(
        learning_rate=0.04, max_iter=200, max_leaf_nodes=10,
        l2_regularization=2.0, random_state=seed,
    ).fit(x, presence, sample_weight=v2.balanced_weights(presence))
    return abundance, positive, classifier


def write_predictions(dataset, models, force):
    abundance_model, positive_model, classifier = models
    pred_dir = dataset["view_dir"] / "predictions"
    pred_dir.mkdir(exist_ok=True)
    paths = {name: pred_dir / filename for name, filename in METHOD_FILES.items()}
    if not force and all(valid_prediction(path, dataset["truth"]) for path in paths.values()):
        return paths, "skipped_existing"

    x = dataset["features"].to_numpy()
    quantitative = v1.apply_local_correction(dataset, abundance_model.predict(x))
    q_target = np.asarray([
        quantitative.at[s, str(dataset["metadata"].at[s, "target_cell_type"])]
        for s in quantitative.index
    ])
    positive = positive_model.predict(x)
    probability = classifier.predict_proba(x)[:, 1]
    outputs = {"CARRliteV2_AbundanceOnly": quantitative}
    for strength in (0.15, 0.30, 0.50):
        desired = v2.soft_presence_fusion(
            dataset, q_target, probability, positive, strength
        )
        outputs["CARRliteV2_HGBC_a{:02d}".format(int(strength * 100))] = (
            v2.set_local_target(dataset, desired)
        )
    for name, frame in outputs.items():
        frame.to_csv(paths[name])
    return paths, "success"


def evaluate_one(args, dataset, method, prediction_path, log_dir):
    if args.skip_evaluation:
        return "skipped", {}
    out_json = (
        dataset["view_dir"] / "evaluation" / method /
        "overall_and_macro_metrics.json"
    )
    command = [
        args.python, args.evaluator,
        "--base_dir", str(dataset["view_dir"]),
        "--prediction", str(prediction_path),
        "--method_name", method,
        "--detection_threshold", "0.005",
        "--fixed_fpr", "0.10",
        "--balanced_repeats", "200",
        "--balance_seed", "2026",
    ]
    log_path = log_dir / "{}_{}.log".format(dataset["scenario_id"], method)
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode != 0 or not out_json.is_file():
        return "failed", {"evaluation_log": str(log_path)}
    with out_json.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    metrics = {}
    metrics.update(payload.get("overall", {}))
    metrics.update(payload.get("rare_macro", {}))
    return "success", metrics


def save_progress(path, rows):
    pd.DataFrame(rows).to_csv(path, index=False)


def main():
    args = parse_args()
    suite_root = Path(args.suite_root)
    manifest = suite_root / "scenario_views" / "scenario_view_manifest.csv"
    evaluator = Path(args.evaluator)
    if not manifest.is_file():
        raise FileNotFoundError(manifest)
    if not args.skip_evaluation and not evaluator.is_file():
        raise FileNotFoundError(evaluator)

    raw_views = read_manifest(manifest)
    if len(raw_views) != 52:
        print("WARNING: expected 52 views, found {}".format(len(raw_views)), flush=True)
    datasets = []
    for i, row in enumerate(raw_views, 1):
        scenario_id = row["scenario_id"]
        view_dir = resolve_view_dir(suite_root, row)
        print("[load {}/{}] {}".format(i, len(raw_views), scenario_id), flush=True)
        datasets.append(build_view_dataset(
            view_dir, scenario_id, args.confusion_k, args.marker_k
        ))

    bases = sorted({d["base"] for d in datasets})
    run_root = suite_root / "batch_runs" / "CARRliteV2"
    log_dir = run_root / "logs"
    run_root.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(exist_ok=True)
    summary_path = run_root / "CARRliteV2_52scenario_summary.csv"
    rows = []
    started = time.time()

    for fold_i, held_out in enumerate(bases, 1):
        train = [d for d in datasets if d["base"] != held_out]
        test = [d for d in datasets if d["base"] == held_out]
        if not train or not test:
            raise RuntimeError("Invalid fold: {}".format(held_out))
        print("\n[fold {}/{}] held out: {}".format(
            fold_i, len(bases), held_out
        ), flush=True)
        models = train_fold(train, args.seed + fold_i)
        for dataset in test:
            paths, run_status = write_predictions(dataset, models, args.force)
            for method, path in paths.items():
                eval_status, metrics = evaluate_one(
                    args, dataset, method, path, log_dir
                )
                row = {
                    "scenario_id": dataset["scenario_id"],
                    "held_out_base": held_out,
                    "depth": dataset["depth"],
                    "method": method,
                    "prediction_path": str(path),
                    "run_status": run_status,
                    "evaluation_status": eval_status,
                }
                row.update(metrics)
                rows.append(row)
                save_progress(summary_path, rows)
                print("  {} / {}: {}".format(
                    dataset["scenario_id"], method, eval_status
                ), flush=True)
                if eval_status == "failed" and args.fail_fast:
                    raise RuntimeError("Evaluation failed; see {}".format(log_dir))

    final = {
        "n_biological_folds": len(bases),
        "n_scenarios": len(datasets),
        "n_methods": len(METHOD_FILES),
        "n_rows": len(rows),
        "n_evaluation_success": sum(
            r["evaluation_status"] == "success" for r in rows
        ),
        "total_elapsed_seconds": time.time() - started,
        "summary_csv": str(summary_path),
    }
    with (run_root / "CARRliteV2_52scenario_run_summary.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(final, handle, ensure_ascii=False, indent=2)
    print("\nFINISHED\n{}".format(json.dumps(final, indent=2)), flush=True)


if __name__ == "__main__":
    main()
