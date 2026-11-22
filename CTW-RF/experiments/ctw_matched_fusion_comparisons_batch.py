#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CTW-RF: matched-fold reliability fusion vs simple/global controls.

Reuses the baseline loading, normalization, and metrics of
global_stacking_cv.py, and the ORIGINAL CTW-RF CV verifier's training-fold
weight algorithms (HardSelect, InvRMSE_p2, SoftOpt), without importing
the legacy module whose top-level code creates directories.

Each seed uses the SAME five test folds for ALL methods. Different
pools are controlled comparisons, NOT independent evaluation datasets.

Predeclared:
 - seeds 2026/2027/2028
 - nested pools strong2 / expanded4 / full6 (from CTW comparator study)
 - baselines: each component method, EqualWeight, GlobalStacking
 - CTW: HardSelect, InvRMSE_p2, SoftOpt (primary historical Proposed_CV)
 - 5 folds per seed/pool, no test targets used in fitting fold weights.

To check inputs without writing: python ctw_matched_fusion_comparisons_batch.py --dry-run
To run all:                     python ctw_matched_fusion_comparisons_batch.py --run

Outputs: summary_metrics_by_seed_pool.csv, metrics_by_fold.csv, weights_by_fold.csv,
         paired_differences_by_seed_pool.csv, fit_runtime_by_fold.csv, run_config.json
Never overwrites any nonempty output directory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.optimize import minimize

import global_stacking_cv as base

HERE = Path(__file__).resolve().parent
BASE_DIR = Path(r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots")
OUT_DIR = Path(r"D:\Research\STdeconv_benchmark\results\CTWRF_matched_fusion_20261122_v1")
SEEDS = (2026, 2027, 2028)
POOLS = {
    "strong2": ("CARD", "cell2location"),
    "expanded4": ("CARD", "cell2location", "RCTD", "SPOTlight"),
    "full6": ("Tangram", "RCTD", "CellDART", "CARD", "cell2location", "SPOTlight"),
}
STRATEGIES = ("EqualWeight", "GlobalStacking", "CTW_HardSelect", "CTW_InvRMSE_p2", "CTW_SoftOpt")
METRICS = ("JSD", "matrix_RMSE", "aggregated_celltype_RMSE", "mean_celltype_RMSE")
EPS = 1e-12


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--run", action="store_true")
    p.add_argument("--base-dir", type=Path, default=BASE_DIR)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return p.parse_args()


def invrmse_weights(predictions, truth, train_idx, power=2.0):
    # Same inverse-RMSE per-celltype definition as historical CTW-RF verifier.
    m, _, n_ct = predictions.shape
    weights = np.empty((m, n_ct), dtype=float)
    for ci in range(n_ct):
        y = truth[train_idx, ci]
        errors = np.array([
            max(float(np.sqrt(np.mean((predictions[mi, train_idx, ci] - y) ** 2))), EPS)
            for mi in range(m)
        ])
        inverse = 1.0 / (errors ** power + EPS)
        weights[:, ci] = inverse / inverse.sum()
    return weights


def hardselect_weights(predictions, truth, train_idx):
    m, _, n_ct = predictions.shape
    weights = np.zeros((m, n_ct), dtype=float)
    for ci in range(n_ct):
        y = truth[train_idx, ci]
        errors = np.array([
            np.sqrt(np.mean((predictions[mi, train_idx, ci] - y) ** 2))
            for mi in range(m)
        ])
        weights[int(np.argmin(errors)), ci] = 1.0
    return weights


def softopt_weights(predictions, truth, train_idx):
    # Exact historical CTW SoftOpt definition: SLSQP per cell type, simplex
    # constraint, initialized with inverse-RMSE p2, 300 maxiter, ftol 1e-12.
    m, _, n_ct = predictions.shape
    prior = invrmse_weights(predictions, truth, train_idx, power=2.0)
    weights = np.zeros((m, n_ct), dtype=float)
    fallback_count = 0
    for ci in range(n_ct):
        X = predictions[:, train_idx, ci].T
        y = truth[train_idx, ci]
        w0 = prior[:, ci].copy()
        def loss(w):
            return float(np.mean((X @ w - y) ** 2))
        opt = minimize(
            loss, w0, method="SLSQP",
            bounds=[(0.0, 1.0)] * m,
            constraints=({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},),
            options={"maxiter": 300, "ftol": 1e-12},
        )
        if opt.success and np.all(np.isfinite(opt.x)):
            w = np.maximum(opt.x, 0)
        else:
            fallback_count += 1
            w = w0
        weights[:, ci] = w / max(float(np.sum(w)), EPS)
    return weights, fallback_count


def fuse_cellwise(predictions, weights, label):
    fused = np.einsum("mnc,mc->nc", predictions, weights)
    return base.normalize(fused, label)


def evaluate_one(seed, pool, method, y, output, folds, fold_rows, summary_rows):
    fields = {"seed": seed, "pool": pool, "n_base_methods": len(POOLS[pool]), "method": method}
    met = base.metric_dict(y, output)
    summary_rows.append({**fields, **met})
    for fid, test in enumerate(folds, 1):
        fold_rows.append({**fields, "fold": fid, "n_test": len(test),
                          **base.metric_dict(y[test], output[test])})


def run_one(seed, pool, methods, y, pred, summary_rows, fold_rows, weights_rows, runtime_rows):
    n = len(y)
    folds = base.make_folds(n, 5, seed)
    predicted = {name: np.empty_like(y) for name in STRATEGIES}
    for fid, test in enumerate(folds, 1):
        train = np.setdiff1d(np.arange(n), test)
        fits = {}
        start = time.perf_counter()
        fits["GlobalStacking"] = base.fit_global_weights(pred[:, train, :], y[train])
        runtime_rows.append({"seed": seed, "pool": pool, "fold": fid,
                             "method": "GlobalStacking", "fit_seconds": time.perf_counter()-start,
                             "optimizer_fallback_celltypes": 0})
        start = time.perf_counter()
        fits["CTW_HardSelect"] = hardselect_weights(pred, y, train)
        runtime_rows.append({"seed": seed, "pool": pool, "fold": fid,
                             "method": "CTW_HardSelect", "fit_seconds": time.perf_counter()-start,
                             "optimizer_fallback_celltypes": 0})
        start = time.perf_counter()
        fits["CTW_InvRMSE_p2"] = invrmse_weights(pred, y, train)
        runtime_rows.append({"seed": seed, "pool": pool, "fold": fid,
                             "method": "CTW_InvRMSE_p2", "fit_seconds": time.perf_counter()-start,
                             "optimizer_fallback_celltypes": 0})
        start = time.perf_counter()
        fits["CTW_SoftOpt"], n_fallback = softopt_weights(pred, y, train)
        runtime_rows.append({"seed": seed, "pool": pool, "fold": fid,
                             "method": "CTW_SoftOpt", "fit_seconds": time.perf_counter()-start,
                             "optimizer_fallback_celltypes": n_fallback})

        predicted["EqualWeight"][test] = np.mean(pred[:, test, :], axis=0)
        predicted["GlobalStacking"][test] = base.fuse(pred[:, test, :], fits["GlobalStacking"])
        for method in ("CTW_HardSelect", "CTW_InvRMSE_p2", "CTW_SoftOpt"):
            predicted[method][test] = fuse_cellwise(pred[:, test, :], fits[method], method)
        for method, w in fits.items():
            if w.ndim == 1:
                for j, source in enumerate(methods):
                    weights_rows.append({"seed": seed, "pool": pool, "fold": fid,
                                         "fusion_method": method, "base_method": source,
                                         "cell_type": "ALL", "weight": float(w[j])})
            else:
                for j, source in enumerate(methods):
                    for ci, ct in enumerate(CELL_TYPES):
                        weights_rows.append({"seed": seed, "pool": pool, "fold": fid,
                                             "fusion_method": method, "base_method": source,
                                             "cell_type": ct, "weight": float(w[j, ci])})

    for label, result in predicted.items():
        if not np.isfinite(result).all() or not np.allclose(result.sum(axis=1), 1.0, atol=1e-6):
            raise ValueError("Invalid CV outputs for " + label)
        evaluate_one(seed, pool, label, y, result, folds, fold_rows, summary_rows)
    for mi, name in enumerate(methods):
        evaluate_one(seed, pool, name, y, pred[mi], folds, fold_rows, summary_rows)
    print("COMPLETED", "seed", seed, "pool", pool,
          "CTW_SoftOpt", round(base.metric_dict(y, predicted["CTW_SoftOpt"])["JSD"], 6),
          "GlobalStacking", round(base.metric_dict(y, predicted["GlobalStacking"])["JSD"], 6),
          "optimizer_fallback_total", int(sum(x["optimizer_fallback_celltypes"] for x in runtime_rows
                                              if x["seed"] == seed and x["pool"] == pool)),
          flush=True)


def main():
    global CELL_TYPES
    args = parse_args()
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        raise FileExistsError("Refusing overwrite: " + str(args.out_dir))
    names = list(base.METHOD_FILES)
    gt, predictions, sources = base.load_inputs(
        args.base_dir / "pseudo_spot_ground_truth.csv", args.base_dir / "predictions", names)
    if len(gt) != 2000 or gt.shape[1] != 19:
        raise ValueError("Unexpected input dataset shape")
    y = gt.to_numpy(dtype=float)
    CELL_TYPES = tuple(gt.columns)
    ix = {m: j for j, m in enumerate(names)}
    print("INPUT CHECK PASS", len(gt), "spots", len(CELL_TYPES),
          "cell types", len(names), "base methods", flush=True)
    print("DESIGN", len(SEEDS), "seeds x", len(POOLS), "method pools =",
          len(SEEDS)*len(POOLS), "matched 5-fold experiments", flush=True)
    if args.dry_run:
        print("DRY RUN PASS — no files written", flush=True)
        return

    summary_rows, fold_rows, weight_rows, runtime_rows = [], [], [], []
    for seed in SEEDS:
        for pool, methods in POOLS.items():
            pred = predictions[[ix[m] for m in methods]]
            run_one(seed, pool, methods, y, pred, summary_rows,
                    fold_rows, weight_rows, runtime_rows)
    summary = pd.DataFrame(summary_rows)
    if len(summary[summary.method.eq("CTW_SoftOpt")]) != 9:
        raise ValueError("Missing CTW_SoftOpt runs")
    pairs = []
    for (seed, pool), group in summary.groupby(["seed", "pool"]):
        ct = group.set_index("method").loc["CTW_SoftOpt"]
        for control in ("GlobalStacking", "EqualWeight", "CTW_HardSelect", "CTW_InvRMSE_p2"):
            other = group.set_index("method").loc[control]
            pairs.append({"seed": seed, "pool": pool, "proposed": "CTW_SoftOpt",
                          "versus": control, **{
                              "delta_" + key: float(ct[key] - other[key]) for key in METRICS
                          }})
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=False)
    summary.to_csv(out / "summary_metrics_by_seed_pool.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(out / "metrics_by_fold.csv", index=False)
    pd.DataFrame(weight_rows).to_csv(out / "weights_by_fold.csv", index=False)
    pd.DataFrame(runtime_rows).to_csv(out / "fit_runtime_by_fold.csv", index=False)
    pd.DataFrame(pairs).to_csv(out / "paired_differences_by_seed_pool.csv", index=False)
    (out / "run_config.json").write_text(json.dumps({
        "status": "exploratory",
        "n_spots": len(y), "n_celltypes": len(CELL_TYPES), "seeds": list(SEEDS),
        "folds": 5, "pools": {k: list(v) for k, v in POOLS.items()},
        "historical_primary": "CTW_SoftOpt (fixed before this batch from archival Proposed_CV)",
        "strategies": list(STRATEGIES), "source_inputs": sources,
        "notes": [
            "Exact same held-out spot indices per seed/pool for all models",
            "CTW weights are fit separately per cell type using only the training folds",
            "SoftOpt reproduces historical verifier SLSQP settings and inverse-RMSE initialization",
            "Prior historical selection of CTW SoftOpt means not an independent final model-selection test",
            "Three random partitions of the same dataset are correlated technical repeats, not biological donors",
            "No separate external reference or independent validation in this batch",
            "No version of original pseudo-spot data or predictions is changed",
        ],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BATCH FINISHED", 9, "matched seed-pool experiments; method summaries", len(summary), flush=True)
    print("OUTPUT", out, flush=True)


if __name__ == "__main__":
    main()
