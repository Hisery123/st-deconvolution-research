#!/usr/bin/env python
"""CARR-lite: confusion-aware local correction for Tangram proportions.

The script supports both the normal 52-scenario directory layout and the small
B01/B08 development bundle.  It never uses held-out ground truth to construct
features or confusion sets.  A biological base scenario is kept wholly out of
training, including all of its sequencing depths.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


DEPTHS = ("010", "025", "050", "100")
EPS = 1e-12


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-root", required=True,
                   help="Directory containing B01_stable_bg3, B08_confusable_bg3, ...")
    p.add_argument("--prediction-root", required=True,
                   help="scenario_views directory, or the flat 8-file development bundle")
    p.add_argument("--bases", nargs="+", default=["B01_stable_bg3", "B08_confusable_bg3"])
    p.add_argument("--out-dir", default="carr_lite_results")
    p.add_argument("--confusion-k", type=int, default=3)
    p.add_argument("--marker-k", type=int, default=40)
    p.add_argument("--ridge-alpha", type=float, default=10.0)
    p.add_argument("--seed", type=int, default=20260724)
    return p.parse_args()


def read_indexed(path: Path) -> pd.DataFrame:
    x = pd.read_csv(path, index_col=0)
    x.index = x.index.astype(str)
    x.columns = x.columns.astype(str)
    return x


def normalize_rows(x: np.ndarray) -> np.ndarray:
    x = np.maximum(np.asarray(x, dtype=np.float64), 0.0)
    return x / np.maximum(x.sum(axis=1, keepdims=True), EPS)


def find_prediction(root: Path, base: str, depth: str) -> Path:
    standard = root / f"{base}_depth_{depth}" / "predictions" / "Tangram_self_benchmark.csv"
    if standard.is_file():
        return standard

    # Names used by the supplied development bundle.
    suffix = "stable" if "stable" in base.lower() else ""
    flat = root / f"Tangram_self_benchmark{depth}{suffix}.csv"
    if flat.is_file():
        return flat

    candidates = list(root.rglob("*.csv"))
    token = re.compile(rf"Tangram_self_benchmark{depth}{suffix}\.csv$", re.I)
    matched = [p for p in candidates if token.search(p.name)]
    if len(matched) == 1:
        return matched[0]
    raise FileNotFoundError(
        f"Cannot uniquely find Tangram prediction for {base}, depth {depth} under {root}"
    )


def reference_profiles(base_dir: Path, genes: pd.Index, cell_types: pd.Index):
    counts = read_indexed(base_dir / "sc_reference_counts.csv")
    labels = pd.read_csv(base_dir / "sc_reference_labels.csv")
    labels.iloc[:, 0] = labels.iloc[:, 0].astype(str)
    label_map = labels.set_index(labels.columns[0])[labels.columns[1]].astype(str)
    counts = counts.loc[counts.index.intersection(label_map.index), genes]
    label_map = label_map.loc[counts.index]
    libnorm = normalize_rows(counts.to_numpy())
    frame = pd.DataFrame(libnorm, index=counts.index, columns=genes)
    frame["_cell_type"] = label_map
    prof = frame.groupby("_cell_type", sort=False).mean()
    missing = cell_types.difference(prof.index)
    if len(missing):
        raise ValueError(f"Reference lacks cell types: {missing.tolist()}")
    return prof.loc[cell_types]


def build_type_definitions(profiles: pd.DataFrame, targets, confusion_k, marker_k):
    z = np.log1p(profiles.to_numpy() * 1e6)
    zc = z - z.mean(axis=1, keepdims=True)
    corr = zc @ zc.T
    corr /= np.maximum(np.linalg.norm(zc, axis=1)[:, None] *
                       np.linalg.norm(zc, axis=1)[None, :], EPS)
    definitions = {}
    for target in targets:
        ti = profiles.index.get_loc(target)
        order = np.argsort(-corr[ti])
        ci = np.array([i for i in order if i != ti][:confusion_k], dtype=int)
        contrast = z[ti] - z[ci].mean(axis=0)
        marker = np.argsort(-contrast)[:marker_k]
        definitions[target] = {
            "target_index": int(ti),
            "confusion_indices": ci,
            "confusion_types": profiles.index[ci].tolist(),
            "marker_indices": marker,
            "reference_similarity_max": float(corr[ti, ci].max()),
            "contrast": contrast,
        }
    return definitions, z


def build_dataset(base: str, depth: str, data_root: Path, pred_root: Path,
                  confusion_k: int, marker_k: int):
    base_dir = data_root / base
    truth = read_indexed(base_dir / "pseudo_spot_ground_truth.csv")
    metadata = read_indexed(base_dir / "spot_metadata.csv")
    prediction = read_indexed(find_prediction(pred_root, base, depth))
    expression = read_indexed(base_dir / f"pseudo_spot_expression_depth_{depth}.csv")

    prediction = prediction.loc[truth.index, truth.columns]
    expression = expression.loc[truth.index]
    metadata = metadata.loc[truth.index]
    prediction.iloc[:, :] = normalize_rows(prediction.to_numpy())

    common_genes = expression.columns
    profiles = reference_profiles(base_dir, common_genes, truth.columns)
    targets = metadata["target_cell_type"].astype(str).drop_duplicates().tolist()
    defs, log_profiles = build_type_definitions(
        profiles, targets, confusion_k=confusion_k, marker_k=marker_k
    )

    observed = normalize_rows(expression.to_numpy())
    observed_log = np.log1p(observed * 1e6)
    pred_arr = prediction.to_numpy()
    reconstructed = pred_arr @ profiles.to_numpy()
    reconstructed_log = np.log1p(np.maximum(reconstructed, 0.0) * 1e6)

    rows, labels = [], []
    for row_i, spot_id in enumerate(truth.index):
        target = str(metadata.at[spot_id, "target_cell_type"])
        d = defs[target]
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
            "base_target_share_local": base_target / max(base_target + conf_values.sum(), EPS),
            "observed_marker_score": obs_marker,
            "observed_marker_margin": obs_marker - conf_marker_ref,
            "marker_fit_target": -abs(obs_marker - target_marker_ref),
            "residual_projection": float(residual @ direction /
                                         max(np.linalg.norm(direction), EPS)),
            "residual_marker_mean": float(residual[mi].mean()),
            "library_size_log": float(np.log1p(expression.iloc[row_i].sum())),
            "reference_similarity_max": d["reference_similarity_max"],
            "depth_fraction": int(depth) / 100.0,
        })
        labels.append(float(truth.iloc[row_i, ti] - base_target))

    features = pd.DataFrame(rows, index=truth.index)
    labels = pd.Series(labels, index=truth.index, name="delta")
    return {
        "base": base, "depth": depth, "truth": truth, "metadata": metadata,
        "prediction": prediction, "features": features, "labels": labels,
        "definitions": defs,
    }


def apply_local_correction(dataset, delta):
    out = dataset["prediction"].to_numpy(copy=True)
    meta = dataset["metadata"]
    columns = dataset["prediction"].columns
    for i, spot_id in enumerate(dataset["prediction"].index):
        target = str(meta.at[spot_id, "target_cell_type"])
        d = dataset["definitions"][target]
        ti, ci = d["target_index"], d["confusion_indices"]
        requested = float(delta[i])
        # Positive correction can only draw mass from the confusion set.
        # Negative correction returns mass to it in proportion to current mass,
        # or uniformly if the confusion set is empty.
        actual = np.clip(requested, -out[i, ti], out[i, ci].sum())
        out[i, ti] += actual
        if actual >= 0:
            weights = out[i, ci] / max(out[i, ci].sum(), EPS)
            out[i, ci] -= actual * weights
        else:
            weights = out[i, ci] / max(out[i, ci].sum(), EPS)
            if out[i, ci].sum() <= EPS:
                weights = np.repeat(1.0 / len(ci), len(ci))
            out[i, ci] += (-actual) * weights
    out = normalize_rows(np.maximum(out, 0.0))
    return pd.DataFrame(out, index=dataset["prediction"].index, columns=columns)


def average_precision(y, score):
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    order = np.argsort(-score, kind="mergesort")
    y, score = y[order], score[order]
    if y.sum() == 0:
        return np.nan
    tp, fp = np.cumsum(y), np.cumsum(1 - y)
    ends = np.r_[score[1:] != score[:-1], True]
    precision = tp[ends] / (tp[ends] + fp[ends])
    recall = tp[ends] / y.sum()
    return float(np.sum((recall - np.r_[0.0, recall[:-1]]) * precision))


def balanced_ap(y, score, seed, repeats=200):
    y, score = np.asarray(y, dtype=int), np.asarray(score, dtype=float)
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    n = min(len(pos), len(neg))
    if n == 0:
        return np.nan
    rng = np.random.RandomState(seed)
    vals = []
    for _ in range(repeats):
        idx = np.r_[rng.choice(pos, n, False), rng.choice(neg, n, False)]
        vals.append(average_precision(y[idx], score[idx]))
    return float(np.mean(vals))


def recall_at_fpr(y, score, max_fpr=0.10):
    y, score = np.asarray(y, dtype=int), np.asarray(score, dtype=float)
    npos, nneg = y.sum(), (1 - y).sum()
    best = 0.0
    for threshold in np.r_[np.inf, np.sort(np.unique(score))[::-1]]:
        selected = score >= threshold
        fpr = np.sum(selected & (y == 0)) / max(nneg, 1)
        recall = np.sum(selected & (y == 1)) / max(npos, 1)
        if fpr <= max_fpr + 1e-12:
            best = max(best, recall)
    return float(best)


def evaluate(dataset, prediction, method, seed):
    truth, meta = dataset["truth"], dataset["metadata"]
    error = prediction.to_numpy() - truth.to_numpy()
    target_errors, labels, scores = [], [], []
    for target in meta["target_cell_type"].astype(str).drop_duplicates():
        mask = meta["target_cell_type"].astype(str).eq(target)
        abundance = meta.loc[mask, "target_abundance"].astype(float)
        rare = abundance.le(0.03)
        labels.extend(abundance.loc[rare].gt(0).astype(int).tolist())
        scores.extend(prediction.loc[mask, target].loc[rare].tolist())
        target_errors.extend(
            (prediction.loc[mask, target] - truth.loc[mask, target]).tolist()
        )
    labels, scores = np.asarray(labels), np.asarray(scores)
    target_errors = np.asarray(target_errors)
    return {
        "held_out_base": dataset["base"], "depth": dataset["depth"], "method": method,
        "matrix_RMSE": float(np.sqrt(np.mean(error ** 2))),
        "target_RMSE": float(np.sqrt(np.mean(target_errors ** 2))),
        "target_MAE": float(np.mean(np.abs(target_errors))),
        "balanced_AUPRC": balanced_ap(labels, scores, seed),
        "recall_at_10pct_FPR": recall_at_fpr(labels, scores),
    }


def main():
    args = parse_args()
    data_root, pred_root = Path(args.data_root), Path(args.prediction_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    datasets = []
    for base in args.bases:
        for depth in DEPTHS:
            print(f"Loading {base}, depth={depth}", flush=True)
            datasets.append(build_dataset(
                base, depth, data_root, pred_root, args.confusion_k, args.marker_k
            ))

    metric_rows, confusion_manifest = [], []
    for held_out in args.bases:
        train = [d for d in datasets if d["base"] != held_out]
        test = [d for d in datasets if d["base"] == held_out]
        if not train:
            raise ValueError("At least two biological base scenarios are required.")
        x_train = pd.concat([d["features"] for d in train]).to_numpy()
        y_train = pd.concat([d["labels"] for d in train]).to_numpy()

        models = {
            "CARR-lite_Ridge": make_pipeline(
                StandardScaler(), Ridge(alpha=args.ridge_alpha)
            ),
            "CARR-lite_HGBR": HistGradientBoostingRegressor(
                learning_rate=0.05, max_iter=200, max_leaf_nodes=15,
                l2_regularization=1.0, random_state=args.seed,
            ),
        }
        for model in models.values():
            model.fit(x_train, y_train)

        fold_dir = out_dir / f"held_out_{held_out}"
        fold_dir.mkdir(exist_ok=True)
        for d in test:
            metric_rows.append(evaluate(
                d, d["prediction"], "Tangram", args.seed + int(d["depth"])
            ))
            for name, model in models.items():
                delta = model.predict(d["features"].to_numpy())
                corrected = apply_local_correction(d, delta)
                corrected.to_csv(fold_dir / f"{name}_{d['depth']}.csv")
                metric_rows.append(evaluate(
                    d, corrected, name, args.seed + int(d["depth"])
                ))
            for target, definition in d["definitions"].items():
                confusion_manifest.append({
                    "held_out_base": held_out, "depth": d["depth"],
                    "target_cell_type": target,
                    "confusion_cell_types": "|".join(definition["confusion_types"]),
                    "reference_similarity_max": definition["reference_similarity_max"],
                })

    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(out_dir / "carr_lite_metrics_by_fold.csv", index=False)
    summary = metrics.groupby(["held_out_base", "method"], as_index=False).agg(
        n_depths=("depth", "count"),
        matrix_RMSE_mean=("matrix_RMSE", "mean"),
        target_RMSE_mean=("target_RMSE", "mean"),
        target_MAE_mean=("target_MAE", "mean"),
        balanced_AUPRC_mean=("balanced_AUPRC", "mean"),
        recall_at_10pct_FPR_mean=("recall_at_10pct_FPR", "mean"),
    )
    summary.to_csv(out_dir / "carr_lite_summary.csv", index=False)
    pd.DataFrame(confusion_manifest).drop_duplicates().to_csv(
        out_dir / "confusion_set_manifest.csv", index=False
    )
    with open(out_dir / "run_config.json", "w", encoding="utf-8") as f:
        json.dump(vars(args), f, ensure_ascii=False, indent=2)
    print("\n" + summary.to_string(index=False), flush=True)
    print(f"\nResults written to: {out_dir.resolve()}", flush=True)


if __name__ == "__main__":
    main()
