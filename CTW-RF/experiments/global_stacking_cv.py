#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run equal-weight and global simplex-stacking baselines on CTW-RF pseudo-spots.

Requires: numpy, pandas, scipy. Never modifies source-snapshot or input CSVs.
Trains a single nonnegative, sum-to-one method weight vector on each training
fold and predicts ONLY the held-out fold. Outputs are exploratory until the
data-generation/reference-cell protocol and external testing are finalized.

Examples:
  python global_stacking_cv.py --selftest
  python global_stacking_cv.py --base-dir "D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots" --dry-run
  python global_stacking_cv.py --base-dir "D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots"
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

METHOD_FILES = {
    "Tangram": "Tangram_self_benchmark.csv",
    "RCTD": "RCTD_self_benchmark.csv",
    "CellDART": "CellDART_self_benchmark.csv",
    "CARD": "CARD_self_benchmark.csv",
    "cell2location": "Cell2location_self_benchmark.csv",
    "SPOTlight": "SPOTlight_self_benchmark.csv",
}
EPS = 1e-12


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-dir", type=Path, help="Pseudo-spot dataset directory")
    p.add_argument("--pred-dir", type=Path, default=None,
                   help="Default: BASE_DIR/predictions")
    p.add_argument("--truth", type=Path, default=None,
                   help="Default: BASE_DIR/pseudo_spot_ground_truth.csv")
    p.add_argument("--out-dir", type=Path, default=None,
                   help="Default: BASE_DIR/experimental_global_stacking")
    p.add_argument("--methods", nargs="+", default=list(METHOD_FILES),
                   choices=list(METHOD_FILES))
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--dry-run", action="store_true",
                   help="Read and validate inputs only; write nothing")
    p.add_argument("--selftest", action="store_true",
                   help="Run synthetic in-memory smoke test; write nothing")
    return p.parse_args()


def canon_col(name):
    name = str(name).strip().replace("_", ".")
    for prefix in (
        r"^meanscell\.abundance\.w\.sf\.",
        r"^means\.cell\.abundance\.w\.sf\.",
        r"^q05cell\.abundance\.w\.sf\.",
        r"^q05\.cell\.abundance\.w\.sf\.",
        r"^q95cell\.abundance\.w\.sf\.",
        r"^q95\.cell\.abundance\.w\.sf\.",
        r"^cell\.abundance\.w\.sf\.",
    ):
        name = re.sub(prefix, "", name, flags=re.IGNORECASE)
    m = re.search(r"L\d+", name)
    return m.group(0) if m else name


def read_matrix(path):
    if not path.is_file():
        raise FileNotFoundError("Missing CSV: " + str(path))
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(str)
    if not df.index.is_unique:
        raise ValueError("Duplicate spot IDs: " + str(path))
    df.columns = [canon_col(c) for c in df.columns]
    df = df.apply(pd.to_numeric, errors="raise")
    if df.columns.duplicated().any():
        # Match the historical CV verifier's duplicate-column aggregation.
        df = df.T.groupby(level=0).sum().T
    if not np.isfinite(df.to_numpy(dtype=float)).all():
        raise ValueError("NaN/Inf in " + str(path))
    return df


def normalize(x, label):
    x = np.asarray(x, dtype=float).copy()
    if np.min(x) < -1e-6:
        raise ValueError("Significant negative values in " + label)
    x[x < 0] = 0
    rows = x.sum(axis=1, keepdims=True)
    if np.any(rows <= EPS):
        raise ValueError("Zero-total spot found in " + label)
    return x / rows


def find_method_path(folder, name):
    nominal = METHOD_FILES[name]
    path = folder / nominal
    if path.is_file():
        return path
    choices = [p for p in folder.glob("*.csv") if p.name.casefold() == nominal.casefold()]
    if len(choices) == 1:
        return choices[0]
    raise FileNotFoundError("Cannot find prediction " + nominal + " in " + str(folder))


def load_inputs(gt_path, pred_dir, methods):
    gt = read_matrix(gt_path)
    gt = pd.DataFrame(normalize(gt.to_numpy(), "ground truth"),
                      index=gt.index, columns=gt.columns)
    if not gt.columns.is_unique:
        raise ValueError("Duplicate cell types in ground truth")
    predictions = []
    sources = {}
    for method in methods:
        path = find_method_path(pred_dir, method)
        df = read_matrix(path)
        if len(df.index) != len(gt.index) or set(df.index) != set(gt.index):
            raise ValueError("Different spot IDs in " + method + "; no silent row filling")
        missing = gt.columns.difference(df.columns)
        if len(missing):
            raise ValueError(method + " missing cell types: " + str(missing.tolist()))
        # Extra columns are ignored, matching prior CTW-RF convention.
        arr = normalize(df.loc[gt.index, gt.columns].to_numpy(), method)
        predictions.append(arr)
        sources[method] = str(path)
    return gt, np.stack(predictions, axis=0), sources


def make_folds(n, k, seed):
    if k < 2 or k > n:
        raise ValueError("folds must be between 2 and number of spots")
    idx = np.arange(n)
    np.random.default_rng(seed).shuffle(idx)
    return np.array_split(idx, k)


def fit_global_weights(p_train, y_train):
    """Convex simplex-constrained least squares on flattened class proportions."""
    try:
        from scipy.optimize import minimize
    except ImportError as e:
        raise RuntimeError("scipy is required for constrained stacking") from e
    m = p_train.shape[0]
    X = p_train.transpose(1, 2, 0).reshape(-1, m)
    y = y_train.reshape(-1)
    w0 = np.full(m, 1.0 / m)
    def loss(w):
        e = X @ w - y
        return float(np.mean(e * e))
    def grad(w):
        e = X @ w - y
        return 2.0 * (X.T @ e) / len(y)
    result = minimize(loss, w0, jac=grad, method="SLSQP",
                      bounds=[(0, 1)] * m,
                      constraints={"type": "eq", "fun": lambda w: np.sum(w) - 1.0,
                                   "jac": lambda w: np.ones_like(w)},
                      options={"maxiter": 1000, "ftol": 1e-13})
    if not result.success:
        raise RuntimeError("Global stacking optimizer failed: " + result.message)
    w = np.clip(result.x, 0, None)
    return w / w.sum()


def fuse(p, weights):
    # Inputs and weights have sums of one; convex mixture retains row sums.
    return np.einsum("mnc,m->nc", p, weights)


def metric_dict(y, p):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    if y.shape != p.shape:
        raise ValueError("Shape mismatch")
    per_ct = np.sqrt(np.mean((p - y) ** 2, axis=0))
    mid = (y + p) / 2
    kl1 = np.sum(np.where(y > 0, y * np.log((y + EPS) / (mid + EPS)), 0), axis=1)
    kl2 = np.sum(np.where(p > 0, p * np.log((p + EPS) / (mid + EPS)), 0), axis=1)
    return {
        "JSD": float(np.mean(0.5 * (kl1 + kl2))),
        "matrix_RMSE": float(np.sqrt(np.mean((p - y) ** 2))),
        "aggregated_celltype_RMSE": float(np.sum(per_ct)),
        "mean_celltype_RMSE": float(np.mean(per_ct)),
    }


def cross_validate(y, p, methods, nfold, seed):
    n = len(y)
    folds = make_folds(n, nfold, seed)
    equal = np.mean(p, axis=0)
    global_oof = np.empty_like(y)
    by_fold, weights = [], []
    for k, test_idx in enumerate(folds, 1):
        train_idx = np.setdiff1d(np.arange(n), test_idx)
        w = fit_global_weights(p[:, train_idx, :], y[train_idx, :])
        global_oof[test_idx, :] = fuse(p[:, test_idx, :], w)
        weights.extend({"fold": k, "method": method, "weight": float(w[j])}
                       for j, method in enumerate(methods))
        for j, method in enumerate(methods):
            by_fold.append({"fold": k, "method": method, "n_test": len(test_idx),
                            **metric_dict(y[test_idx], p[j, test_idx])})
        by_fold.append({"fold": k, "method": "EqualWeight", "n_test": len(test_idx),
                        **metric_dict(y[test_idx], equal[test_idx])})
        by_fold.append({"fold": k, "method": "GlobalStacking", "n_test": len(test_idx),
                        **metric_dict(y[test_idx], global_oof[test_idx])})
    summary = []
    for j, method in enumerate(methods):
        summary.append({"method": method, **metric_dict(y, p[j])})
    summary.append({"method": "EqualWeight", **metric_dict(y, equal)})
    summary.append({"method": "GlobalStacking", **metric_dict(y, global_oof)})
    return (pd.DataFrame(summary), pd.DataFrame(by_fold),
            pd.DataFrame(weights), global_oof)


def selftest():
    rng = np.random.default_rng(11)
    y = rng.dirichlet([1, 2, 3], size=24)
    good = normalize(0.9 * y + 0.1 / 3, "good")
    bad = np.tile(np.array([[0.8, 0.1, 0.1]]), (len(y), 1))
    p = np.stack([good, bad])
    summary, folds, weights, oof = cross_validate(y, p, ["good", "bad"], 4, 2026)
    assert len(folds) == 4 * 4
    assert np.isfinite(oof).all()
    assert np.allclose(oof.sum(axis=1), 1)
    assert np.allclose(weights.groupby("fold")["weight"].sum().values, 1)
    assert summary.loc[summary.method.eq("GlobalStacking"), "matrix_RMSE"].iloc[0] <= (
        summary.loc[summary.method.eq("EqualWeight"), "matrix_RMSE"].iloc[0] + 1e-7)
    print("SELFTEST PASS")


def main():
    args = parse_args()
    if args.selftest:
        selftest()
        return
    if args.base_dir is None:
        raise SystemExit("--base-dir is required unless --selftest")
    base = args.base_dir
    gt_path = args.truth or (base / "pseudo_spot_ground_truth.csv")
    pred_dir = args.pred_dir or (base / "predictions")
    out_dir = args.out_dir or (base / "experimental_global_stacking")
    if len(set(args.methods)) != len(args.methods) or len(args.methods) < 2:
        raise ValueError("Supply at least two distinct methods")
    gt, p, sources = load_inputs(gt_path, pred_dir, args.methods)
    print("Inputs ready:", len(gt), "spots,", gt.shape[1], "cell types;",
          "methods:", ", ".join(args.methods))
    if args.dry_run:
        print("DRY RUN PASS (no files written)")
        return
    summary, fold_metrics, fold_weights, global_oof = cross_validate(
        gt.to_numpy(), p, args.methods, args.folds, args.seed
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_dir / "metrics_overall.csv", index=False)
    fold_metrics.to_csv(out_dir / "metrics_by_fold.csv", index=False)
    fold_weights.to_csv(out_dir / "global_weights_by_fold.csv", index=False)
    pd.DataFrame(global_oof, index=gt.index, columns=gt.columns).to_csv(
        out_dir / "global_stacking_oof.csv")
    config = {"status": "exploratory", "seed": args.seed, "nfold": args.folds,
              "ground_truth": str(gt_path), "predictions": sources,
              "n_spots": len(gt), "n_celltypes": gt.shape[1],
              "methods": args.methods,
              "warning": "Not a final independent test; no raw-data/reference audit"}
    (out_dir / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))
    print("WROTE", out_dir)


if __name__ == "__main__":
    main()
