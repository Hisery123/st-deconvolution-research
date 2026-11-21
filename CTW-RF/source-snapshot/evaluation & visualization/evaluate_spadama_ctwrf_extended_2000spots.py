# -*- coding: utf-8 -*-
"""
Evaluate SpaDAMA and rebuild CTW-RF with SpaDAMA included.

Purpose:
1. Add SpaDAMA_self_benchmark.csv into the previous benchmark statistics.
2. Recompute metrics for all baselines.
3. Build CTW-RF-extended by adding SpaDAMA into the candidate method pool.
4. Save summary tables and simple figures.

Input prediction files:
D:/Research/STdeconv_benchmark/data/groundtruth/self_benchmark_cortex_svz_2000spots/predictions/
    Tangram_self_benchmark.csv
    RCTD_self_benchmark.csv
    CellDART_self_benchmark.csv
    CARD_self_benchmark.csv
    Cell2location_self_benchmark.csv
    SPOTlight_self_benchmark.csv
    SpaDAMA_self_benchmark.csv

Optional previous CTW-RF file:
    Proposed_CV_best_self_benchmark.csv
or
    Proposed_best_self_benchmark.csv

Outputs:
D:/Research/STdeconv_benchmark/evaluation & visualization/ctwrf_extended_spadama_2000spots/

Run:
python "D:/Research/STdeconv_benchmark/evaluation & visualization/evaluate_spadama_ctwrf_extended_2000spots.py"
"""

import os
import json
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. Paths
# ============================================================
BASE_DIR = r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots"
PRED_DIR = os.path.join(BASE_DIR, "predictions")
GT_PATH = os.path.join(BASE_DIR, "pseudo_spot_ground_truth.csv")

OUT_DIR = r"D:\Research\STdeconv_benchmark\evaluation & visualization\ctwrf_extended_spadama_2000spots"
os.makedirs(OUT_DIR, exist_ok=True)

SEED = 2026
N_FOLDS = 5
EPS = 1e-12

# Candidate pool for CTW-RF-extended.
# The file names follow your current benchmark convention.
BASELINE_FILES = {
    "Tangram": "Tangram_self_benchmark.csv",
    "RCTD": "RCTD_self_benchmark.csv",
    "CellDART": "CellDART_self_benchmark.csv",
    "CARD": "CARD_self_benchmark.csv",
    "cell2location": "Cell2location_self_benchmark.csv",
    "SPOTlight": "SPOTlight_self_benchmark.csv",
    "SpaDAMA": "SpaDAMA_self_benchmark.csv",
}

# Optional old CTW-RF prediction, only for comparison, not used as a candidate.
OLD_CTWRF_CANDIDATES = [
    "Proposed_CV_best_self_benchmark.csv",
    "Proposed_best_self_benchmark.csv",
    "CTW_RF_self_benchmark.csv",
    "CTW-RF_self_benchmark.csv",
]


# ============================================================
# 2. Utilities
# ============================================================
def read_matrix(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(str)
    df.columns = df.columns.astype(str)
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    df[df < 0] = 0.0
    return df


def row_normalize(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy().astype(float)
    x = x.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    x[x < 0] = 0.0
    s = x.sum(axis=1)
    s[s == 0] = 1.0
    return x.div(s, axis=0)


def align_prediction(pred: pd.DataFrame, gt: pd.DataFrame) -> pd.DataFrame:
    pred = pred.copy()
    pred.index = pred.index.astype(str)
    pred.columns = pred.columns.astype(str)

    # Align spots.
    common_spots = gt.index.intersection(pred.index)
    if len(common_spots) == 0:
        raise ValueError("No common spots between prediction and ground truth.")

    # Keep ground truth order.
    pred = pred.loc[common_spots]
    gt_use = gt.loc[common_spots]

    # Align cell-type columns. Missing columns are filled with zero.
    aligned = pd.DataFrame(0.0, index=gt_use.index, columns=gt_use.columns)
    common_cols = [c for c in gt_use.columns if c in pred.columns]
    aligned.loc[:, common_cols] = pred.loc[:, common_cols].values

    return row_normalize(aligned)


def jsd_score(pred: pd.DataFrame, gt: pd.DataFrame, eps: float = EPS) -> float:
    p = pred.values.astype(float)
    q = gt.values.astype(float)
    p = np.clip(p, eps, None)
    q = np.clip(q, eps, None)
    p = p / p.sum(axis=1, keepdims=True)
    q = q / q.sum(axis=1, keepdims=True)
    m = 0.5 * (p + q)
    kl_pm = np.sum(p * np.log(p / m), axis=1)
    kl_qm = np.sum(q * np.log(q / m), axis=1)
    return float(np.mean(0.5 * (kl_pm + kl_qm)))


def matrix_rmse(pred: pd.DataFrame, gt: pd.DataFrame) -> float:
    return float(np.sqrt(np.mean((pred.values - gt.values) ** 2)))


def per_celltype_rmse(pred: pd.DataFrame, gt: pd.DataFrame) -> pd.Series:
    vals = {}
    for c in gt.columns:
        vals[c] = float(np.sqrt(np.mean((pred[c].values - gt[c].values) ** 2)))
    return pd.Series(vals)


def evaluate_prediction(name: str, pred: pd.DataFrame, gt: pd.DataFrame) -> dict:
    ct = per_celltype_rmse(pred, gt)
    out = {
        "method": name,
        "JSD": jsd_score(pred, gt),
        "matrix_RMSE": matrix_rmse(pred, gt),
        "aggregated_celltype_RMSE": float(ct.sum()),
        "mean_celltype_RMSE": float(ct.mean()),
    }
    for c, v in ct.items():
        out[c] = v
    return out


def make_folds(n: int, n_folds: int, seed: int):
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    return np.array_split(idx, n_folds)


def solve_simplex_weights(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Minimize ||Xw - y||^2 subject to w >= 0 and sum(w)=1.

    Uses scipy SLSQP if available.
    Falls back to inverse-RMSE weights if scipy is unavailable.
    """
    m = X.shape[1]

    # Remove invalid rows.
    mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
    X = X[mask]
    y = y[mask]

    if X.shape[0] == 0:
        return np.ones(m) / m

    try:
        from scipy.optimize import minimize

        def obj(w):
            r = X @ w - y
            return float(np.mean(r * r))

        cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
        bounds = [(0.0, 1.0)] * m
        w0 = np.ones(m) / m

        res = minimize(obj, w0, method="SLSQP", bounds=bounds, constraints=cons,
                       options={"maxiter": 500, "ftol": 1e-12, "disp": False})
        if res.success and np.all(np.isfinite(res.x)):
            w = np.maximum(res.x, 0.0)
            if w.sum() > 0:
                return w / w.sum()

    except Exception as e:
        print("[WARN] scipy SLSQP failed or unavailable; fallback to inv-RMSE weights:", repr(e))

    # Fallback: inverse RMSE per method.
    rmses = []
    for j in range(m):
        rmse = np.sqrt(np.mean((X[:, j] - y) ** 2))
        rmses.append(rmse)
    rmses = np.asarray(rmses)
    inv = 1.0 / (rmses + 1e-8)
    if inv.sum() <= 0 or not np.isfinite(inv).all():
        return np.ones(m) / m
    return inv / inv.sum()


def fit_ctwrf_cv(preds: dict, gt: pd.DataFrame, n_folds: int = 5, seed: int = 2026):
    """
    5-fold CV CTW-RF:
    - For each fold, learn cell-type-specific weights on training spots.
    - Predict held-out spots by weighted fusion.
    """
    methods = list(preds.keys())
    spots = gt.index.tolist()
    cell_types = gt.columns.tolist()
    n = len(spots)
    m = len(methods)
    cnum = len(cell_types)

    # Stack predictions as [method, spot, celltype]
    arr = np.stack([preds[name].loc[spots, cell_types].values for name in methods], axis=0)
    y = gt.loc[spots, cell_types].values

    folds = make_folds(n, n_folds, seed)
    pred_out = np.zeros((n, cnum), dtype=float)
    weight_folds = []

    for fold_id, test_idx in enumerate(folds, start=1):
        train_mask = np.ones(n, dtype=bool)
        train_mask[test_idx] = False
        train_idx = np.where(train_mask)[0]

        W = np.zeros((m, cnum), dtype=float)
        for ci in range(cnum):
            X_train = arr[:, train_idx, ci].T  # [n_train, m]
            y_train = y[train_idx, ci]
            W[:, ci] = solve_simplex_weights(X_train, y_train)

        # Predict test fold.
        # pred for each cell type = sum_m w_m,c * pred_m
        for ci in range(cnum):
            pred_out[test_idx, ci] = arr[:, test_idx, ci].T @ W[:, ci]

        weight_folds.append(pd.DataFrame(W, index=methods, columns=cell_types))
        print(f"[CV] fold {fold_id}/{n_folds} done")

    pred_df = pd.DataFrame(pred_out, index=spots, columns=cell_types)
    pred_df = row_normalize(pred_df)

    avg_weights = sum(weight_folds) / len(weight_folds)

    return pred_df, avg_weights, weight_folds


def load_all_predictions(gt: pd.DataFrame):
    preds = {}
    missing = []

    for name, fname in BASELINE_FILES.items():
        path = os.path.join(PRED_DIR, fname)
        if os.path.exists(path):
            pred_raw = read_matrix(path)
            preds[name] = align_prediction(pred_raw, gt)
            print("[LOAD]", name, pred_raw.shape, "->", preds[name].shape)
        else:
            missing.append((name, path))

    if missing:
        print("\n[WARN] Missing prediction files:")
        for name, path in missing:
            print("  ", name, path)

    return preds


def load_old_ctwrf(gt: pd.DataFrame):
    for fname in OLD_CTWRF_CANDIDATES:
        path = os.path.join(PRED_DIR, fname)
        if os.path.exists(path):
            pred = align_prediction(read_matrix(path), gt)
            print("[LOAD old CTW-RF]", fname, "->", pred.shape)
            return pred
    print("[INFO] Old CTW-RF prediction not found. Skip old CTW-RF comparison.")
    return None


def plot_bar(metrics: pd.DataFrame, col: str, title: str, ylabel: str, out_png: str):
    order = metrics.sort_values(col).index.tolist()
    vals = metrics.loc[order, col].values
    colors = []
    for m in order:
        if "CTW-RF" in m:
            colors.append("#C8374A")
        elif m == "SpaDAMA":
            colors.append("#E68632")
        else:
            colors.append("#BFC5CE")

    plt.figure(figsize=(10, 4.8))
    x = np.arange(len(order))
    plt.bar(x, vals, color=colors)
    plt.xticks(x, order, rotation=35, ha="right")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(axis="y", alpha=0.25)
    for i, v in enumerate(vals):
        plt.text(i, v + max(vals) * 0.015, f"{v:.4f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()


def plot_scatter(metrics: pd.DataFrame, out_png: str):
    plt.figure(figsize=(7, 5.5))
    for m, row in metrics.iterrows():
        if "CTW-RF" in m:
            color = "#C8374A"
            size = 90
        elif m == "SpaDAMA":
            color = "#E68632"
            size = 70
        else:
            color = "#BFC5CE"
            size = 55
        plt.scatter(row["JSD"], row["aggregated_celltype_RMSE"], s=size, color=color, edgecolor="black", linewidth=0.4)
        plt.text(row["JSD"] + 0.002, row["aggregated_celltype_RMSE"], m, fontsize=9, va="center")
    plt.xlabel("JSD (lower is better)")
    plt.ylabel("Aggregated cell-type RMSE (lower is better)")
    plt.title("Performance trade-off with SpaDAMA")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()


# ============================================================
# 3. Main
# ============================================================
def main():
    print("============================================================")
    print("Evaluate SpaDAMA and CTW-RF-extended on self2000")
    print("============================================================")
    print("BASE_DIR:", BASE_DIR)
    print("PRED_DIR:", PRED_DIR)
    print("OUT_DIR:", OUT_DIR)

    gt = read_matrix(GT_PATH)
    gt = row_normalize(gt)
    gt.index = gt.index.astype(str)
    gt.columns = gt.columns.astype(str)

    preds = load_all_predictions(gt)

    if "SpaDAMA" not in preds:
        raise FileNotFoundError(
            "SpaDAMA_self_benchmark.csv not found in predictions directory. "
            "Please run SpaDAMA adapter first."
        )

    # Build CTW-RF-extended with SpaDAMA included.
    print("\n[CTW-RF-extended] fitting 5-fold CV fusion with candidates:")
    print(list(preds.keys()))
    ctwrf_ext, avg_weights, weight_folds = fit_ctwrf_cv(preds, gt, n_folds=N_FOLDS, seed=SEED)

    ext_pred_path = os.path.join(PRED_DIR, "CTW_RF_extended_SpaDAMA_self_benchmark.csv")
    ctwrf_ext.to_csv(ext_pred_path)
    avg_weights.to_csv(os.path.join(OUT_DIR, "weights_CTW_RF_extended_SpaDAMA_average.csv"))
    for i, w in enumerate(weight_folds, start=1):
        w.to_csv(os.path.join(OUT_DIR, f"weights_CTW_RF_extended_SpaDAMA_fold{i}.csv"))

    # Evaluate baselines, old CTW-RF if present, and new extended CTW-RF.
    eval_preds = dict(preds)

    old_ctwrf = load_old_ctwrf(gt)
    if old_ctwrf is not None:
        eval_preds["CTW-RF"] = old_ctwrf

    eval_preds["CTW-RF+SpaDAMA"] = ctwrf_ext

    records = []
    for name, pred in eval_preds.items():
        records.append(evaluate_prediction(name, pred, gt))

    all_metrics = pd.DataFrame(records).set_index("method")

    # Add ranks based on major metrics.
    all_metrics["JSD_rank"] = all_metrics["JSD"].rank(method="min", ascending=True).astype(int)
    all_metrics["aggregated_RMSE_rank"] = all_metrics["aggregated_celltype_RMSE"].rank(method="min", ascending=True).astype(int)
    all_metrics["mean_rank"] = all_metrics[["JSD_rank", "aggregated_RMSE_rank"]].mean(axis=1)

    # Sort table by mean_rank then aggregated RMSE.
    sorted_metrics = all_metrics.sort_values(["mean_rank", "aggregated_celltype_RMSE", "JSD"])

    all_metrics.to_csv(os.path.join(OUT_DIR, "01_metrics_all_methods_with_spadama.csv"))
    sorted_metrics.to_csv(os.path.join(OUT_DIR, "02_main_comparison_with_spadama.csv"))

    # Save compact table.
    compact_cols = [
        "JSD",
        "matrix_RMSE",
        "aggregated_celltype_RMSE",
        "mean_celltype_RMSE",
        "JSD_rank",
        "aggregated_RMSE_rank",
        "mean_rank",
    ]
    sorted_metrics[compact_cols].to_csv(os.path.join(OUT_DIR, "Table1_with_SpaDAMA_and_CTWRF_extended.csv"))

    # Simple figures.
    plot_bar(
        sorted_metrics,
        "JSD",
        "JSD comparison with SpaDAMA",
        "JSD (lower is better)",
        os.path.join(OUT_DIR, "Fig_JSD_with_SpaDAMA.png"),
    )
    plot_bar(
        sorted_metrics,
        "aggregated_celltype_RMSE",
        "Aggregated cell-type RMSE comparison with SpaDAMA",
        "Aggregated cell-type RMSE (lower is better)",
        os.path.join(OUT_DIR, "Fig_aggregated_RMSE_with_SpaDAMA.png"),
    )
    plot_scatter(sorted_metrics, os.path.join(OUT_DIR, "Fig_tradeoff_with_SpaDAMA.png"))

    # Summary.
    summary = {
        "best_by_JSD": sorted_metrics["JSD"].idxmin(),
        "best_by_aggregated_celltype_RMSE": sorted_metrics["aggregated_celltype_RMSE"].idxmin(),
        "SpaDAMA": sorted_metrics.loc["SpaDAMA", compact_cols].to_dict(),
        "CTW-RF+SpaDAMA": sorted_metrics.loc["CTW-RF+SpaDAMA", compact_cols].to_dict(),
    }
    with open(os.path.join(OUT_DIR, "summary_with_SpaDAMA.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n[Main comparison]")
    print(sorted_metrics[compact_cols])

    print("\nSaved CTW-RF-extended prediction:")
    print(ext_pred_path)

    print("\nSaved outputs to:")
    print(OUT_DIR)
    print("============================================================")
    print("DONE")
    print("============================================================")


if __name__ == "__main__":
    main()
