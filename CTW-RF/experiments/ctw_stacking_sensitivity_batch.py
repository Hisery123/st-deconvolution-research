#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CTW-RF extension: batched GlobalStacking sensitivity on existing predictions.

This is a GLOBAL stacking comparator study, not a reimplementation or rerun
of CTW-RF Proposed_CV. Uses the original global_stacking_cv.py metrics,
normalization and SLSQP weights, with matched 5-fold partitions per seed.

Prespecified exploratory grid:
  seeds: 2026, 2027, 2028 (different spot-level fold assignments)
  method pools: strong2, expanded4, full6 (nested method subsets)
  calibration views per training fold: 100, 200, 500, all
Thus 3*3*4=36 configurations x 5 folds (180 optimization fits).
Repeated folds and pseudo-spots are NOT independent biological replication.
The strong2 pool is informed by prior observed results, not an unbiased
independent test of subset selection.

Examples:
  python ctw_stacking_sensitivity_batch.py --dry-run
  python ctw_stacking_sensitivity_batch.py --run
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd

import global_stacking_cv as stacking

DEFAULT_BASE = Path(r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots")
DEFAULT_OUT = Path(r"D:\Research\STdeconv_benchmark\results\CTWRF_stacking_sensitivity_20261122_v1")
SEEDS = (2026, 2027, 2028)
BUDGETS = (100, 200, 500, "all")
POOLS = {
    "strong2": ("CARD", "cell2location"),
    "expanded4": ("CARD", "cell2location", "RCTD", "SPOTlight"),
    "full6": ("Tangram", "RCTD", "CellDART", "CARD", "cell2location", "SPOTlight"),
}
METRICS = ("JSD", "matrix_RMSE", "aggregated_celltype_RMSE", "mean_celltype_RMSE")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--run", action="store_true")
    p.add_argument("--base-dir", type=Path, default=DEFAULT_BASE)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--folds", type=int, default=5)
    return p.parse_args()


def evaluate_config(y, p, methods, folds, seed, budget):
    oof = np.empty_like(y)
    equal = np.mean(p, axis=0)
    fold_rows = []
    weight_rows = []
    start = time.perf_counter()
    for fid, test in enumerate(folds, 1):
        train = np.setdiff1d(np.arange(len(y)), test)
        shuffled = np.random.default_rng(seed * 1000 + fid).permutation(train)
        used = shuffled if budget == "all" else shuffled[:int(budget)]
        if len(used) < 2:
            raise ValueError("Too few train spots")
        w = stacking.fit_global_weights(p[:, used], y[used])
        pred = stacking.fuse(p[:, test], w)
        oof[test] = pred
        weight_rows.extend({"fold": fid, "method": name, "weight": float(w[j]),
                            "n_calibration": len(used)}
                           for j, name in enumerate(methods))
        for label, pred_fold in (("EqualWeight", equal[test]),
                                 ("GlobalStacking", pred)):
            fold_rows.append({"fold": fid, "method": label,
                              "n_test": len(test), "n_calibration": len(used),
                              **stacking.metric_dict(y[test], pred_fold)})
    elapsed = time.perf_counter() - start
    if not np.isfinite(oof).all() or not np.allclose(oof.sum(axis=1), 1.0, atol=1e-6):
        raise ValueError("Invalid OOF prediction")
    run_rows = [
        {"method": "EqualWeight", "elapsed_seconds": elapsed,
         **stacking.metric_dict(y, equal)},
        {"method": "GlobalStacking", "elapsed_seconds": elapsed,
         **stacking.metric_dict(y, oof)},
    ]
    return run_rows, fold_rows, weight_rows


def main():
    args = parse_args()
    path = args.base_dir
    if args.folds != 5:
        raise ValueError("This preregistered batch uses exactly five folds")
    truth_path, predictions_path = path / "pseudo_spot_ground_truth.csv", path / "predictions"
    names = list(stacking.METHOD_FILES)
    gt, predictions, sources = stacking.load_inputs(truth_path, predictions_path, names)
    y = gt.to_numpy(dtype=float)
    index = {m: i for i, m in enumerate(names)}
    if y.shape[0] < 1000:
        raise ValueError("Too few spots for a 500-training-spot budget")
    if set(POOLS["expanded4"]) - set(POOLS["full6"]) or set(POOLS["strong2"]) - set(POOLS["expanded4"]):
        raise ValueError("Candidate pools should be nested")
    print("INPUT CHECK PASS", y.shape[0], "spots", y.shape[1], "cell types", len(names), "methods", flush=True)
    print("DESIGN", len(SEEDS), "seeds x", len(POOLS), "method pools x", len(BUDGETS),
          "budgets =", len(SEEDS) * len(POOLS) * len(BUDGETS), "configurations", flush=True)
    if args.dry_run:
        for pool, methods in POOLS.items():
            print("POOL", pool, ",".join(methods), flush=True)
        print("DRY RUN PASS — no files written", flush=True)
        return
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        raise FileExistsError("Refusing to overwrite existing sensitivity results: " + str(args.out_dir))

    runs, folds_out, weights_out = [], [], []
    for seed in SEEDS:
        fold_ids = stacking.make_folds(len(y), args.folds, seed)
        for pool, names_pool in POOLS.items():
            p = predictions[[index[name] for name in names_pool]]
            for budget in BUDGETS:
                run_rows, fold_rows, weight_rows = evaluate_config(
                    y, p, names_pool, fold_ids, seed, budget)
                fields = {"seed": seed, "pool": pool, "n_methods": len(names_pool),
                          "calibration_budget": str(budget)}
                runs.extend({**fields, **row} for row in run_rows)
                folds_out.extend({**fields, **row} for row in fold_rows)
                weights_out.extend({**fields, **row} for row in weight_rows)
                report = next(r for r in run_rows if r["method"] == "GlobalStacking")
                print("COMPLETED", seed, pool, budget,
                      "JSD", round(report["JSD"], 6),
                      "matrix_RMSE", round(report["matrix_RMSE"], 6),
                      flush=True)
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(runs)
    if len(df) != len(SEEDS) * len(POOLS) * len(BUDGETS) * 2:
        raise ValueError("Unexpected number of summary records")
    df.to_csv(out / "metrics_by_seed_pool_budget.csv", index=False)
    pd.DataFrame(folds_out).to_csv(out / "metrics_by_fold.csv", index=False)
    pd.DataFrame(weights_out).to_csv(out / "weights_by_fold.csv", index=False)
    df.groupby(["pool", "calibration_budget", "method"], as_index=False)[list(METRICS)].mean().to_csv(
        out / "descriptive_means_across_seeds.csv", index=False)
    cfg = {"status": "exploratory", "analysis": "global stacking comparator sensitivity only",
           "dataset": str(path), "source_predictions": sources,
           "n_spots": len(y), "n_types": y.shape[1], "folds": args.folds,
           "seeds": list(SEEDS), "budgets": [str(x) for x in BUDGETS],
           "pools": {k: list(v) for k, v in POOLS.items()},
           "notes": ["Prespecified source-matched fit/evaluation with no test-fold labels used for weights",
                     "Prior results informed strong2 selection: exploratory, not independent tuning",
                     "Changing spot-level split seeds does not produce independent biological replicates",
                     "No CTW-RF Proposed_CV re-evaluation: this is global stacking robustness only",
                     "Raw-reference-cell overlap and publication validity still need final audit"]}
    (out / "run_config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BATCH FINISHED", len(SEEDS)*len(POOLS)*len(BUDGETS), "configurations", flush=True)
    print("OUTPUT", out, flush=True)


if __name__ == "__main__":
    main()
