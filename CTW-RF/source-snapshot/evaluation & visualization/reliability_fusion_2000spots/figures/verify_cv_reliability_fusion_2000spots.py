# -*- coding: utf-8 -*-
"""
Dedicated 5-fold CV verification script for CTW-RF / reliability-aware fusion.

Purpose:
1. Read ground truth and six baseline prediction CSVs for self_benchmark_cortex_svz_2000spots.
2. Align all methods by ground-truth spot IDs and cell-type columns.
3. Check row normalization and missing columns/spots.
4. Learn cell-type-wise fusion weights on training folds only.
5. Predict held-out folds and merge all folds into CV predictions.
6. Report JSD, matrix_RMSE, aggregated cell-type RMSE, per-cell-type RMSE,
   and winner counts.

Run:
python "D:/Research/STdeconv_benchmark/evaluation & visualization/verify_cv_reliability_fusion_2000spots.py"

Default data path:
D:/Research/STdeconv_benchmark/data/groundtruth/self_benchmark_cortex_svz_2000spots
"""

import os
import re
import json
import warnings
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 0. Configuration
# ============================================================
SEED = 2026
N_FOLDS = 5
EPS = 1e-12

BASE_DIR = r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots"
PRED_DIR = os.path.join(BASE_DIR, "predictions")
GT_PATH = os.path.join(BASE_DIR, "pseudo_spot_ground_truth.csv")

EVAL_DIR = r"D:\Research\STdeconv_benchmark\evaluation & visualization\reliability_fusion_2000spots_cv_verify"
FIG_DIR = os.path.join(EVAL_DIR, "figures")
os.makedirs(EVAL_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(PRED_DIR, exist_ok=True)

METHOD_SPECS = {
    "Tangram": ["Tangram_self_benchmark.csv"],
    "RCTD": ["RCTD_self_benchmark.csv"],
    "CellDART": ["CellDART_self_benchmark.csv"],
    "CARD": ["CARD_self_benchmark.csv"],
    "cell2location": ["Cell2location_self_benchmark.csv", "cell2location_self_benchmark.csv"],
    "SPOTlight": ["SPOTlight_self_benchmark.csv", "SPOTlight_self_benchmark.csv"],
}

INVRMSE_POWERS = [1.0, 2.0, 4.0, 8.0]
MIN_COMMON_SPOT_RATIO = 0.90

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except Exception as e:
    SCIPY_AVAILABLE = False
    minimize = None
    warnings.warn("scipy is not available; SoftOpt will be skipped. " + repr(e))


# ============================================================
# 1. Basic utilities
# ============================================================
def normalize_celltype_names(cols: List[str]) -> List[str]:
    out = []
    for x in cols:
        s = str(x).strip()
        s = s.replace("_", ".")
        prefixes = [
            r"^meanscell\.abundance\.w\.sf\.",
            r"^means\.cell\.abundance\.w\.sf\.",
            r"^q05cell\.abundance\.w\.sf\.",
            r"^q05\.cell\.abundance\.w\.sf\.",
            r"^q95cell\.abundance\.w\.sf\.",
            r"^q95\.cell\.abundance\.w\.sf\.",
            r"^cell\.abundance\.w\.sf\.",
        ]
        for p in prefixes:
            s = re.sub(p, "", s, flags=re.IGNORECASE)
        m = re.search(r"L\d+", s)
        if m:
            s = m.group(0)
        out.append(s)
    return out


def read_csv_matrix(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(str)
    df.columns = [str(c) for c in df.columns]
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return df


def collapse_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.columns.duplicated().any():
        df = df.T.groupby(level=0).sum().T
    return df


def row_normalize(arr: np.ndarray) -> np.ndarray:
    x = np.asarray(arr, dtype=float).copy()
    x[~np.isfinite(x)] = 0.0
    x[x < 0] = 0.0
    s = x.sum(axis=1, keepdims=True)
    s[~np.isfinite(s)] = 0.0
    s[s <= EPS] = 1.0
    x = x / s
    x[~np.isfinite(x)] = 0.0
    return x


def find_file(directory: str, names: List[str]) -> Optional[str]:
    for name in names:
        p = os.path.join(directory, name)
        if os.path.exists(p):
            return p
    if not os.path.isdir(directory):
        return None
    lower_map = {x.lower(): x for x in os.listdir(directory)}
    for name in names:
        real = lower_map.get(name.lower())
        if real:
            return os.path.join(directory, real)
    return None


def prepare_gt(path: str) -> pd.DataFrame:
    gt = read_csv_matrix(path)
    gt.columns = normalize_celltype_names(list(gt.columns))
    gt = collapse_duplicate_columns(gt)
    gt = pd.DataFrame(row_normalize(gt.values), index=gt.index, columns=gt.columns)
    return gt


def prepare_prediction(path: str, gt: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    raw = read_csv_matrix(path)
    raw_orig_shape = raw.shape
    raw.columns = normalize_celltype_names(list(raw.columns))
    raw = collapse_duplicate_columns(raw)
    raw[raw < 0] = 0.0
    raw = raw.fillna(0.0)

    common_spots = gt.index.intersection(raw.index)
    common_ratio = len(common_spots) / max(len(gt.index), 1)
    if common_ratio < MIN_COMMON_SPOT_RATIO:
        raise ValueError(
            f"Too few common spots: {len(common_spots)} / {len(gt.index)} "
            f"for {path}"
        )

    aligned = pd.DataFrame(0.0, index=gt.index, columns=gt.columns)
    common_cols = [c for c in gt.columns if c in raw.columns]
    aligned.loc[common_spots, common_cols] = raw.loc[common_spots, common_cols].values
    aligned = pd.DataFrame(row_normalize(aligned.values), index=aligned.index, columns=aligned.columns)

    report = {
        "file": path,
        "raw_rows": raw_orig_shape[0],
        "raw_cols": raw_orig_shape[1],
        "common_spots": len(common_spots),
        "gt_spots": len(gt.index),
        "common_spot_ratio": common_ratio,
        "common_celltypes": len(common_cols),
        "gt_celltypes": len(gt.columns),
        "missing_celltypes": ";".join([c for c in gt.columns if c not in raw.columns]),
        "extra_celltypes": ";".join([c for c in raw.columns if c not in gt.columns]),
        "row_sum_min_after_norm": float(aligned.sum(axis=1).min()),
        "row_sum_max_after_norm": float(aligned.sum(axis=1).max()),
    }
    return aligned, report


# ============================================================
# 2. Metrics
# ============================================================
def jsd_one(p: np.ndarray, q: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = np.maximum(p, 0)
    q = np.maximum(q, 0)
    ps = p.sum()
    qs = q.sum()
    if ps <= EPS:
        p = np.ones_like(p) / len(p)
    else:
        p = p / ps
    if qs <= EPS:
        q = np.ones_like(q) / len(q)
    else:
        q = q / qs
    m = 0.5 * (p + q)
    kl_pm = np.sum(np.where(p > 0, p * np.log((p + EPS) / (m + EPS)), 0.0))
    kl_qm = np.sum(np.where(q > 0, q * np.log((q + EPS) / (m + EPS)), 0.0))
    return float(0.5 * (kl_pm + kl_qm))


def calc_metrics(pred: pd.DataFrame, gt: pd.DataFrame) -> dict:
    p = row_normalize(pred.loc[gt.index, gt.columns].values)
    y = row_normalize(gt.values)

    per_ct_rmse = np.sqrt(np.mean((p - y) ** 2, axis=0))
    jsd = float(np.mean([jsd_one(p[i], y[i]) for i in range(y.shape[0])]))
    matrix_rmse = float(np.sqrt(np.mean((p - y) ** 2)))
    agg_ct_rmse = float(np.sum(per_ct_rmse))
    mean_ct_rmse = float(np.mean(per_ct_rmse))

    out = {
        "JSD": jsd,
        "matrix_RMSE": matrix_rmse,
        "aggregated_celltype_RMSE": agg_ct_rmse,
        "mean_celltype_RMSE": mean_ct_rmse,
    }
    for ct, v in zip(gt.columns, per_ct_rmse):
        out[ct] = float(v)
    return out


# ============================================================
# 3. Fusion weights
# ============================================================
def per_celltype_rmse_weights(pred_tensor: np.ndarray, gt_arr: np.ndarray, train_idx: np.ndarray, power: float) -> np.ndarray:
    # pred_tensor shape=(M,N,C), gt=(N,C), return weights shape=(M,C)
    M, _, C = pred_tensor.shape
    weights = np.zeros((M, C), dtype=float)
    for c in range(C):
        err = []
        y = gt_arr[train_idx, c]
        for m in range(M):
            x = pred_tensor[m, train_idx, c]
            rmse = float(np.sqrt(np.mean((x - y) ** 2)))
            err.append(max(rmse, EPS))
        inv = 1.0 / (np.asarray(err) ** power + EPS)
        weights[:, c] = inv / inv.sum()
    return weights


def hardselect_weights(pred_tensor: np.ndarray, gt_arr: np.ndarray, train_idx: np.ndarray) -> np.ndarray:
    M, _, C = pred_tensor.shape
    weights = np.zeros((M, C), dtype=float)
    for c in range(C):
        rmses = []
        y = gt_arr[train_idx, c]
        for m in range(M):
            x = pred_tensor[m, train_idx, c]
            rmses.append(float(np.sqrt(np.mean((x - y) ** 2))))
        best = int(np.argmin(rmses))
        weights[best, c] = 1.0
    return weights


def softopt_weights(pred_tensor: np.ndarray, gt_arr: np.ndarray, train_idx: np.ndarray, init_weights: Optional[np.ndarray] = None) -> np.ndarray:
    if not SCIPY_AVAILABLE:
        return per_celltype_rmse_weights(pred_tensor, gt_arr, train_idx, power=2.0)

    M, _, C = pred_tensor.shape
    weights = np.zeros((M, C), dtype=float)
    bounds = [(0.0, 1.0)] * M
    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)

    for c in range(C):
        X = pred_tensor[:, train_idx, c].T  # n_train x M
        y = gt_arr[train_idx, c]
        if init_weights is not None:
            w0 = init_weights[:, c].astype(float)
            if w0.sum() <= EPS:
                w0 = np.ones(M) / M
            else:
                w0 = w0 / w0.sum()
        else:
            w0 = np.ones(M) / M

        def objective(w):
            pred = X.dot(w)
            return float(np.mean((pred - y) ** 2))

        res = minimize(objective, w0, method="SLSQP", bounds=bounds, constraints=cons, options={"maxiter": 300, "ftol": 1e-12})
        if res.success and np.all(np.isfinite(res.x)):
            w = np.maximum(res.x, 0.0)
        else:
            w = w0
        weights[:, c] = w / max(w.sum(), EPS)
    return weights


def apply_weights(pred_tensor: np.ndarray, weights: np.ndarray, index: pd.Index, columns: pd.Index) -> pd.DataFrame:
    # weights shape=(M,C). Weighted sum per cell type.
    fused = np.einsum("mnc,mc->nc", pred_tensor, weights)
    fused = row_normalize(fused)
    return pd.DataFrame(fused, index=index, columns=columns)


def make_folds(n: int, k: int, seed: int) -> List[np.ndarray]:
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    return [np.sort(x) for x in np.array_split(idx, k)]


def cv_predict(pred_tensor: np.ndarray, gt_arr: np.ndarray, index: pd.Index, columns: pd.Index, strategy: str, power: float = 2.0):
    n = gt_arr.shape[0]
    folds = make_folds(n, N_FOLDS, SEED)
    out = np.zeros_like(gt_arr, dtype=float)
    fold_rows = []
    fold_weights = []

    for f, test_idx in enumerate(folds, start=1):
        train_idx = np.setdiff1d(np.arange(n), test_idx)
        if strategy == "HardSelect":
            w = hardselect_weights(pred_tensor, gt_arr, train_idx)
        elif strategy == "InvRMSE":
            w = per_celltype_rmse_weights(pred_tensor, gt_arr, train_idx, power=power)
        elif strategy == "SoftOpt":
            init = per_celltype_rmse_weights(pred_tensor, gt_arr, train_idx, power=2.0)
            w = softopt_weights(pred_tensor, gt_arr, train_idx, init_weights=init)
        else:
            raise ValueError(strategy)

        pred_fold = np.einsum("mnc,mc->nc", pred_tensor[:, test_idx, :], w)
        pred_fold = row_normalize(pred_fold)
        out[test_idx, :] = pred_fold
        fold_weights.append(w)

        fold_df = pd.DataFrame(pred_fold, index=index[test_idx], columns=columns)
        fold_gt = pd.DataFrame(gt_arr[test_idx, :], index=index[test_idx], columns=columns)
        met = calc_metrics(fold_df, fold_gt)
        met["fold"] = f
        met["strategy"] = strategy if strategy != "InvRMSE" else f"InvRMSE_p{power:g}"
        met["n_test"] = len(test_idx)
        fold_rows.append(met)

    out = row_normalize(out)
    out_df = pd.DataFrame(out, index=index, columns=columns)
    avg_w = np.mean(np.stack(fold_weights, axis=0), axis=0)
    return out_df, avg_w, fold_rows


# ============================================================
# 4. Plotting
# ============================================================
def save_bar(df: pd.DataFrame, metric: str, title: str, filename: str):
    methods = list(df.index)
    vals = df[metric].values
    x = np.arange(len(methods))
    plt.figure(figsize=(max(9, len(methods) * 1.15), 4.8))
    plt.bar(x, vals)
    plt.xticks(x, methods, rotation=25, ha="right")
    plt.ylabel(metric + " (lower is better)")
    plt.title(title)
    for i, v in enumerate(vals):
        if np.isfinite(v):
            plt.text(i, v, f"{v:.4f}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=300)
    plt.close()


def save_heatmap(mat_df: pd.DataFrame, title: str, filename: str):
    plt.figure(figsize=(max(10, mat_df.shape[1] * 0.55), max(4, mat_df.shape[0] * 0.35)))
    im = plt.imshow(mat_df.values, aspect="auto")
    plt.yticks(range(mat_df.shape[0]), mat_df.index)
    plt.xticks(range(mat_df.shape[1]), mat_df.columns, rotation=45, ha="right")
    plt.colorbar(im, label="weight")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=300)
    plt.close()


# ============================================================
# 5. Main
# ============================================================
def main():
    np.random.seed(SEED)
    gt = prepare_gt(GT_PATH)
    print("GT:", gt.shape, "row sum range:", gt.sum(axis=1).min(), gt.sum(axis=1).max())

    preds: Dict[str, pd.DataFrame] = {}
    reports = []
    for name, candidates in METHOD_SPECS.items():
        path = find_file(PRED_DIR, candidates)
        if path is None:
            print(f"[WARN] missing method: {name} candidates={candidates}")
            continue
        pred, rep = prepare_prediction(path, gt)
        rep["method"] = name
        preds[name] = pred
        reports.append(rep)
        print("Loaded", name, pred.shape, "from", path)

    if len(preds) < 2:
        raise RuntimeError("Need at least two baseline predictions.")

    report_df = pd.DataFrame(reports).set_index("method")
    report_df.to_csv(os.path.join(EVAL_DIR, "00_alignment_report.csv"), encoding="utf-8-sig")

    method_names = list(preds.keys())
    pred_tensor = np.stack([preds[m].loc[gt.index, gt.columns].values for m in method_names], axis=0)
    gt_arr = gt.values

    all_predictions: Dict[str, pd.DataFrame] = {m: preds[m] for m in method_names}
    weight_outputs: Dict[str, np.ndarray] = {}
    fold_rows = []

    # Full-data candidates, mainly used as upper bound.
    full_idx = np.arange(gt.shape[0])
    w_hard = hardselect_weights(pred_tensor, gt_arr, full_idx)
    all_predictions["Proposed_HardSelect_full"] = apply_weights(pred_tensor, w_hard, gt.index, gt.columns)
    weight_outputs["Proposed_HardSelect_full"] = w_hard

    for p in INVRMSE_POWERS:
        w_inv = per_celltype_rmse_weights(pred_tensor, gt_arr, full_idx, power=p)
        key = f"Proposed_InvRMSE_p{p:g}_full"
        all_predictions[key] = apply_weights(pred_tensor, w_inv, gt.index, gt.columns)
        weight_outputs[key] = w_inv

    w_init = per_celltype_rmse_weights(pred_tensor, gt_arr, full_idx, power=2.0)
    w_soft = softopt_weights(pred_tensor, gt_arr, full_idx, init_weights=w_init)
    all_predictions["Proposed_SoftOpt_full"] = apply_weights(pred_tensor, w_soft, gt.index, gt.columns)
    weight_outputs["Proposed_SoftOpt_full"] = w_soft

    # 5-fold CV candidates.
    cv_candidates = []
    for strategy in ["HardSelect", "SoftOpt"]:
        pred_cv, w_cv, rows = cv_predict(pred_tensor, gt_arr, gt.index, gt.columns, strategy=strategy)
        key = f"Proposed_{strategy}_5foldCV"
        all_predictions[key] = pred_cv
        weight_outputs[key] = w_cv
        fold_rows.extend(rows)
        cv_candidates.append(key)

    for p in INVRMSE_POWERS:
        pred_cv, w_cv, rows = cv_predict(pred_tensor, gt_arr, gt.index, gt.columns, strategy="InvRMSE", power=p)
        key = f"Proposed_InvRMSE_p{p:g}_5foldCV"
        all_predictions[key] = pred_cv
        weight_outputs[key] = w_cv
        fold_rows.extend(rows)
        cv_candidates.append(key)

    # Metrics.
    metrics = []
    for name, pred in all_predictions.items():
        met = calc_metrics(pred, gt)
        met["method"] = name
        if name in method_names:
            met["group"] = "baseline"
        elif name.endswith("5foldCV"):
            met["group"] = "proposed_cv"
        else:
            met["group"] = "proposed_full"
        metrics.append(met)
    metrics_df = pd.DataFrame(metrics).set_index("method")

    # Ranking columns.
    metrics_df["JSD_rank"] = metrics_df["JSD"].rank(method="min")
    metrics_df["aggregated_celltype_RMSE_rank"] = metrics_df["aggregated_celltype_RMSE"].rank(method="min")
    metrics_df["mean_rank"] = metrics_df[["JSD_rank", "aggregated_celltype_RMSE_rank"]].mean(axis=1)
    metrics_df = metrics_df.sort_values(["group", "aggregated_celltype_RMSE", "JSD"])
    metrics_df.to_csv(os.path.join(EVAL_DIR, "01_metrics_all_methods.csv"), encoding="utf-8-sig")

    fold_df = pd.DataFrame(fold_rows)
    fold_df.to_csv(os.path.join(EVAL_DIR, "02_cv_fold_metrics.csv"), index=False, encoding="utf-8-sig")

    # Choose best CV by primary metric; best full as upper bound.
    cv_metrics = metrics_df[metrics_df["group"] == "proposed_cv"].copy()
    full_metrics = metrics_df[metrics_df["group"] == "proposed_full"].copy()
    best_cv = cv_metrics.sort_values(["aggregated_celltype_RMSE", "JSD"]).index[0]
    best_full = full_metrics.sort_values(["aggregated_celltype_RMSE", "JSD"]).index[0]

    # Save predictions.
    for name in [best_cv, best_full]:
        all_predictions[name].to_csv(os.path.join(PRED_DIR, f"{name}_self_benchmark.csv"))
    all_predictions[best_cv].to_csv(os.path.join(PRED_DIR, "Proposed_CV_best_self_benchmark.csv"))
    all_predictions[best_full].to_csv(os.path.join(PRED_DIR, "Proposed_full_best_self_benchmark.csv"))

    # Save weights.
    for name, w in weight_outputs.items():
        wdf = pd.DataFrame(w, index=method_names, columns=gt.columns)
        wdf.to_csv(os.path.join(EVAL_DIR, f"weights_{name}.csv"), encoding="utf-8-sig")
    pd.DataFrame(weight_outputs[best_cv], index=method_names, columns=gt.columns).to_csv(
        os.path.join(EVAL_DIR, "weights_Proposed_CV_best.csv"), encoding="utf-8-sig"
    )
    pd.DataFrame(weight_outputs[best_full], index=method_names, columns=gt.columns).to_csv(
        os.path.join(EVAL_DIR, "weights_Proposed_full_best.csv"), encoding="utf-8-sig"
    )

    # Main display tables.
    best_baseline_by_rmse = metrics_df[metrics_df["group"] == "baseline"].sort_values("aggregated_celltype_RMSE").index[0]
    best_baseline_by_jsd = metrics_df[metrics_df["group"] == "baseline"].sort_values("JSD").index[0]
    main_methods = method_names + [best_cv]
    main_df = metrics_df.loc[main_methods].copy()
    main_df = main_df.rename(index={best_cv: "Proposed_CV"})
    main_df.to_csv(os.path.join(EVAL_DIR, "03_main_cv_comparison.csv"), encoding="utf-8-sig")

    # Improvements relative to best baseline.
    base_rmse = metrics_df.loc[best_baseline_by_rmse, "aggregated_celltype_RMSE"]
    base_jsd = metrics_df.loc[best_baseline_by_jsd, "JSD"]
    improve_rows = []
    for name in main_methods:
        improve_rows.append({
            "method": "Proposed_CV" if name == best_cv else name,
            "JSD_improvement_vs_best_baseline_percent": (base_jsd - metrics_df.loc[name, "JSD"]) / base_jsd * 100.0,
            "RMSE_improvement_vs_best_baseline_percent": (base_rmse - metrics_df.loc[name, "aggregated_celltype_RMSE"]) / base_rmse * 100.0,
            "best_baseline_by_JSD": best_baseline_by_jsd,
            "best_baseline_by_RMSE": best_baseline_by_rmse,
        })
    pd.DataFrame(improve_rows).set_index("method").to_csv(
        os.path.join(EVAL_DIR, "04_main_cv_improvement_vs_best_baseline.csv"), encoding="utf-8-sig"
    )

    # Cell-type winner count for main CV comparison.
    celltypes = list(gt.columns)
    per_ct = main_df[celltypes].copy()
    winners = per_ct.idxmin(axis=0)
    winners = winners.replace({best_cv: "Proposed_CV"})
    winner_count = winners.value_counts().rename_axis("method").reset_index(name="n_best_celltypes")
    winner_count.to_csv(os.path.join(EVAL_DIR, "05_cv_celltype_winner_count.csv"), index=False, encoding="utf-8-sig")

    # Plots.
    display_df = main_df.rename(index={best_cv: "Proposed_CV"})
    save_bar(display_df, "JSD", "5-fold CV reliability fusion: JSD", "01_cv_JSD_barplot.png")
    save_bar(display_df, "aggregated_celltype_RMSE", "5-fold CV reliability fusion: aggregated cell-type RMSE", "02_cv_aggregated_celltype_RMSE_barplot.png")

    plt.figure(figsize=(7.2, 5.4))
    for name, row in display_df.iterrows():
        plt.scatter(row["JSD"], row["aggregated_celltype_RMSE"], s=80)
        plt.text(row["JSD"], row["aggregated_celltype_RMSE"], " " + name, va="center")
    plt.xlabel("JSD (lower is better)")
    plt.ylabel("aggregated cell-type RMSE (lower is better)")
    plt.title("5-fold CV performance trade-off")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "03_cv_JSD_RMSE_scatter.png"), dpi=300)
    plt.close()

    # Per cell-type heatmap for main methods.
    plt.figure(figsize=(max(10, len(celltypes) * 0.55), max(4, len(display_df) * 0.4)))
    im = plt.imshow(display_df[celltypes].values, aspect="auto")
    plt.yticks(range(len(display_df)), display_df.index)
    plt.xticks(range(len(celltypes)), celltypes, rotation=45, ha="right")
    plt.colorbar(im, label="cell-type RMSE")
    plt.title("5-fold CV cell-type RMSE heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "04_cv_celltype_RMSE_heatmap.png"), dpi=300)
    plt.close()

    weight_df = pd.DataFrame(weight_outputs[best_cv], index=method_names, columns=gt.columns)
    save_heatmap(weight_df, "Average CV fusion weights", "05_cv_weight_heatmap.png")

    # Summary txt.
    summary_path = os.path.join(EVAL_DIR, "06_cv_verification_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("CTW-RF / reliability fusion 5-fold CV verification\n")
        f.write("=" * 70 + "\n")
        f.write(f"BASE_DIR: {BASE_DIR}\n")
        f.write(f"GT: {GT_PATH}\n")
        f.write(f"n_spots: {gt.shape[0]}\n")
        f.write(f"n_celltypes: {gt.shape[1]}\n")
        f.write(f"methods: {', '.join(method_names)}\n")
        f.write(f"scipy_available: {SCIPY_AVAILABLE}\n\n")
        f.write(f"Best baseline by JSD: {best_baseline_by_jsd} ({metrics_df.loc[best_baseline_by_jsd, 'JSD']:.6f})\n")
        f.write(f"Best baseline by aggregated cell-type RMSE: {best_baseline_by_rmse} ({metrics_df.loc[best_baseline_by_rmse, 'aggregated_celltype_RMSE']:.6f})\n\n")
        f.write(f"Best full-data proposed upper bound: {best_full}\n")
        f.write(f"  JSD = {metrics_df.loc[best_full, 'JSD']:.6f}\n")
        f.write(f"  aggregated_celltype_RMSE = {metrics_df.loc[best_full, 'aggregated_celltype_RMSE']:.6f}\n\n")
        f.write(f"Best 5-fold CV proposed: {best_cv}\n")
        f.write(f"  JSD = {metrics_df.loc[best_cv, 'JSD']:.6f}\n")
        f.write(f"  aggregated_celltype_RMSE = {metrics_df.loc[best_cv, 'aggregated_celltype_RMSE']:.6f}\n")
        f.write(f"  JSD improvement vs best baseline = {(base_jsd - metrics_df.loc[best_cv, 'JSD']) / base_jsd * 100.0:.2f}%\n")
        f.write(f"  RMSE improvement vs best baseline = {(base_rmse - metrics_df.loc[best_cv, 'aggregated_celltype_RMSE']) / base_rmse * 100.0:.2f}%\n\n")
        f.write("Cell-type winner count in main CV comparison:\n")
        f.write(winner_count.to_string(index=False))
        f.write("\n")

    print("\nDONE 5-fold CV verification")
    print("Best full-data proposed:", best_full)
    print(metrics_df.loc[best_full, ["JSD", "aggregated_celltype_RMSE", "matrix_RMSE"]])
    print("\nBest 5-fold CV proposed:", best_cv)
    print(metrics_df.loc[best_cv, ["JSD", "aggregated_celltype_RMSE", "matrix_RMSE"]])
    print("\nBest baseline by RMSE:", best_baseline_by_rmse)
    print(metrics_df.loc[best_baseline_by_rmse, ["JSD", "aggregated_celltype_RMSE", "matrix_RMSE"]])
    print("\nOutputs saved to:", EVAL_DIR)
    print("Figures saved to:", FIG_DIR)
    print("Prediction saved to:", os.path.join(PRED_DIR, "Proposed_CV_best_self_benchmark.csv"))


if __name__ == "__main__":
    main()
