# -*- coding: utf-8 -*-
"""
Ablation and candidate-pool robustness analysis for CTW-RF
on self_benchmark_cortex_svz_2000spots.

This script adds two groups of experiments:

A. Fusion strategy ablation
   Compare:
   - Best single baseline
   - SimpleAverage
   - GlobalInvRMSE
   - CellTypeHardSelect
   - CellTypeInvRMSE
   - CTW-RF
   - CTW-RF+SpaDAMA+SpaJoint

B. Candidate-pool robustness
   Compare CTW-RF after removing one candidate method at a time:
   - Full pool
   - w/o Tangram
   - w/o RCTD
   - w/o CellDART
   - w/o CARD
   - w/o cell2location
   - w/o SPOTlight
   - w/o SpaDAMA
   - w/o SpaJoint

Run:
python "D:/Research/STdeconv_benchmark/evaluation & visualization/run_ctwr_ablation_robustness_2000spots.py"
"""

import os
import re
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 0. Paths
# ============================================================
BASE_DIR = r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots"
PRED_DIR = os.path.join(BASE_DIR, "predictions")
GT_PATH = os.path.join(BASE_DIR, "pseudo_spot_ground_truth.csv")

OUT_DIR = r"D:\Research\STdeconv_benchmark\evaluation & visualization\ctwr_ablation_robustness_2000spots"
FIG_DIR = os.path.join(OUT_DIR, "figures")
PRED_OUT_DIR = os.path.join(OUT_DIR, "predictions")
WEIGHT_OUT_DIR = os.path.join(OUT_DIR, "weights")

for d in [OUT_DIR, FIG_DIR, PRED_OUT_DIR, WEIGHT_OUT_DIR]:
    os.makedirs(d, exist_ok=True)

SEED = 2026
N_FOLDS = 5
EPS = 1e-12


# ============================================================
# 1. Prediction files
# ============================================================
PRED_FILE_CANDIDATES = {
    "Tangram": ["Tangram_self_benchmark.csv"],
    "RCTD": ["RCTD_self_benchmark.csv"],
    "CellDART": ["CellDART_self_benchmark.csv"],
    "CARD": ["CARD_self_benchmark.csv"],
    "cell2location": ["Cell2location_self_benchmark.csv", "cell2location_self_benchmark.csv"],
    "SPOTlight": ["SPOTlight_self_benchmark.csv"],
    "SpaDAMA": ["SpaDAMA_self_benchmark.csv"],
    "SpaJoint": ["SpaJoint_self_benchmark.csv", "SpaJoint_100ep_50iters_generic_self2000_benchmark.csv"],
}

CORE_METHODS = ["Tangram", "RCTD", "CellDART", "CARD", "cell2location", "SPOTlight"]
EXTENDED_METHODS = ["Tangram", "RCTD", "CellDART", "CARD", "cell2location", "SPOTlight", "SpaDAMA", "SpaJoint"]


# ============================================================
# 2. Display
# ============================================================
DISPLAY_NAME = {
    "BestSingle": "Best single baseline",
    "SimpleAverage": "Simple average",
    "GlobalInvRMSE": "Global InvRMSE",
    "CellTypeHardSelect": "Cell-type HardSelect",
    "CellTypeInvRMSE": "Cell-type InvRMSE",
    "CTW-RF": "CTW-RF",
    "CTW-RF+SpaDAMA+SpaJoint": "CTW-RF+SpaJoint",
    "SpaDAMA": "SpaDAMA",
    "SpaJoint": "SpaJoint",
    "cell2location": "cell2location",
    "Tangram": "Tangram",
    "RCTD": "RCTD",
    "CellDART": "CellDART",
    "CARD": "CARD",
    "SPOTlight": "SPOTlight",
}

COLORS = {
    "CTW-RF": "#4C78A8",
    "CTW-RF+SpaDAMA+SpaJoint": "#C7354A",
    "SpaDAMA": "#F28E2B",
    "SpaJoint": "#8E6C8A",
    "BestSingle": "#7F7F7F",
    "SimpleAverage": "#BFC5CE",
    "GlobalInvRMSE": "#BFC5CE",
    "CellTypeHardSelect": "#BFC5CE",
    "CellTypeInvRMSE": "#BFC5CE",
}
DEFAULT_COLOR = "#C5CBD3"


def color_for(name):
    return COLORS.get(name, DEFAULT_COLOR)


def display(name):
    return DISPLAY_NAME.get(name, name)


# ============================================================
# 3. IO and alignment
# ============================================================
def find_first_existing(pred_dir, candidates):
    for fname in candidates:
        path = os.path.join(pred_dir, fname)
        if os.path.exists(path):
            return path
    return None


def read_matrix(path):
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(str)
    df.columns = df.columns.astype(str)
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    df[df < 0] = 0.0
    return df


def row_normalize(df):
    x = df.copy().astype(float)
    x = x.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    x[x < 0] = 0.0
    s = x.sum(axis=1)
    s[s == 0] = 1.0
    return x.div(s, axis=0)


def normalize_col_name(c):
    """
    Map columns such as meanscell_abundance_w_sf_L10 to L10.
    """
    c0 = str(c).strip().replace(" ", "").replace("-", "_")
    m = re.search(r"(L\d+)", c0)
    if m is not None:
        return m.group(1)

    prefixes = [
        "gt_", "GT_", "pred_", "Pred_", "prediction_",
        "celltype_", "CellType_", "prop_", "proportion_",
        "meanscell_abundance_w_sf_", "means_cell_abundance_w_sf_",
        "q05cell_abundance_w_sf_", "q95cell_abundance_w_sf_",
    ]

    changed = True
    while changed:
        changed = False
        for p in prefixes:
            if c0.startswith(p):
                c0 = c0[len(p):]
                changed = True
    return c0


def canonicalize_columns(pred, gt_cols, method_name):
    gt_cols = [str(c) for c in gt_cols]
    gt_set = set(gt_cols)

    rename = {}
    for c in pred.columns:
        nc = normalize_col_name(c)
        if nc in gt_set:
            rename[c] = nc

    pred2 = pred.rename(columns=rename)

    if pred2.columns.duplicated().any():
        pred2 = pred2.T.groupby(level=0).mean().T

    common_cols = [c for c in gt_cols if c in pred2.columns]

    report = {
        "method": method_name,
        "raw_shape": str(pred.shape),
        "raw_cols_head": list(pred.columns[:12]),
        "renamed_n": len(rename),
        "common_n": len(common_cols),
        "common_cols": common_cols,
    }

    if len(common_cols) == 0 and pred2.shape[1] == len(gt_cols):
        numeric_like = all(str(c).strip().isdigit() for c in pred2.columns)
        if numeric_like:
            pred2.columns = gt_cols
            common_cols = gt_cols[:]
            report["fallback"] = "numeric_columns_assigned_by_gt_order"

    report["final_common_n"] = len(common_cols)
    return pred2, report


def align_prediction(raw, gt, method_name):
    raw = raw.copy()
    raw.index = raw.index.astype(str)
    raw.columns = raw.columns.astype(str)

    pred, report = canonicalize_columns(raw, gt.columns, method_name)

    common_spots = gt.index.intersection(pred.index)
    if len(common_spots) == 0:
        if pred.shape[0] == gt.shape[0]:
            pred.index = gt.index
            common_spots = gt.index
            report["spot_fallback"] = "same_row_count_assigned_gt_index"
        else:
            raise ValueError(f"[{method_name}] no common spots. pred={pred.shape}, gt={gt.shape}")

    common_cols = [c for c in gt.columns if c in pred.columns]
    if len(common_cols) == 0:
        raise ValueError(
            f"[{method_name}] no common cell-type columns. "
            f"raw cols head={list(raw.columns[:20])}, gt cols={list(gt.columns)}"
        )

    aligned = pd.DataFrame(0.0, index=gt.loc[common_spots].index, columns=gt.columns)
    aligned.loc[:, common_cols] = pred.loc[common_spots, common_cols].values
    aligned = row_normalize(aligned)

    report["aligned_shape"] = str(aligned.shape)
    report["missing_gt_cols"] = [c for c in gt.columns if c not in common_cols]
    return aligned, report


def load_predictions(gt):
    preds = {}
    reports = {}

    print("[Load predictions]")
    for method, candidates in PRED_FILE_CANDIDATES.items():
        path = find_first_existing(PRED_DIR, candidates)
        if path is None:
            print("[MISS]", method, candidates)
            continue

        raw = read_matrix(path)
        pred, report = align_prediction(raw, gt, method)
        report["path"] = path

        preds[method] = pred
        reports[method] = report

        print(
            "[LOAD]",
            method,
            raw.shape,
            "->",
            pred.shape,
            "| common cols:",
            report["final_common_n"],
            "|",
            os.path.basename(path),
        )

    with open(os.path.join(OUT_DIR, "alignment_report_ablation.json"), "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)

    return preds, reports


# ============================================================
# 4. Metrics
# ============================================================
def jsd_score(pred, gt):
    p = pred.values.astype(float)
    q = gt.values.astype(float)

    p = np.clip(p, EPS, None)
    q = np.clip(q, EPS, None)

    p = p / p.sum(axis=1, keepdims=True)
    q = q / q.sum(axis=1, keepdims=True)

    m = 0.5 * (p + q)

    kl_pm = np.sum(p * np.log(p / m), axis=1)
    kl_qm = np.sum(q * np.log(q / m), axis=1)

    return float(np.mean(0.5 * (kl_pm + kl_qm)))


def matrix_rmse(pred, gt):
    return float(np.sqrt(np.mean((pred.values - gt.values) ** 2)))


def per_celltype_rmse(pred, gt):
    out = {}
    for c in gt.columns:
        out[c] = float(np.sqrt(np.mean((pred[c].values - gt[c].values) ** 2)))
    return pd.Series(out)


def evaluate_prediction(name, pred, gt):
    pred = pred.loc[gt.index, gt.columns]
    pred = row_normalize(pred)
    ct = per_celltype_rmse(pred, gt)

    rec = {
        "method": name,
        "JSD": jsd_score(pred, gt),
        "matrix_RMSE": matrix_rmse(pred, gt),
        "aggregated_celltype_RMSE": float(ct.sum()),
        "mean_celltype_RMSE": float(ct.mean()),
    }
    for c, v in ct.items():
        rec[c] = float(v)
    return rec


# ============================================================
# 5. Cross-validation and fusion
# ============================================================
def make_folds(n, n_folds=N_FOLDS, seed=SEED):
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    return np.array_split(idx, n_folds)


def get_arrays(preds, methods, gt):
    spots = gt.index.tolist()
    cell_types = gt.columns.tolist()
    arr = np.stack(
        [preds[m].loc[spots, cell_types].values.astype(float) for m in methods],
        axis=0,
    )
    y = gt.loc[spots, cell_types].values.astype(float)
    return arr, y, spots, cell_types


def solve_simplex_weights(X, y):
    """
    CTW-RF weight solver:
    minimize mean((Xw-y)^2) subject to w>=0 and sum(w)=1.

    Uses scipy.optimize.SLSQP if available.
    Falls back to inverse RMSE weights if scipy fails.
    """
    m = X.shape[1]
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

        res = minimize(
            obj,
            w0,
            method="SLSQP",
            bounds=bounds,
            constraints=cons,
            options={"maxiter": 500, "ftol": 1e-12, "disp": False},
        )

        if res.success and np.all(np.isfinite(res.x)):
            w = np.maximum(res.x, 0.0)
            if w.sum() > 0:
                return w / w.sum()

    except Exception as e:
        warnings.warn("SLSQP failed; fallback to inverse RMSE weights: " + repr(e))

    rmses = np.sqrt(np.mean((X - y.reshape(-1, 1)) ** 2, axis=0))
    inv = 1.0 / (rmses + 1e-8)
    if not np.all(np.isfinite(inv)) or inv.sum() <= 0:
        return np.ones(m) / m
    return inv / inv.sum()


def fit_cv_fusion(preds, methods, gt, strategy, n_folds=N_FOLDS, seed=SEED):
    """
    strategy:
    - SimpleAverage
    - GlobalInvRMSE
    - CellTypeHardSelect
    - CellTypeInvRMSE
    - CTW-RF
    """
    arr, y, spots, cell_types = get_arrays(preds, methods, gt)

    n_methods = len(methods)
    n_spots = len(spots)
    n_celltypes = len(cell_types)

    # Simple average does not use labels.
    if strategy == "SimpleAverage":
        pred = arr.mean(axis=0)
        W = pd.DataFrame(
            np.ones((n_methods, n_celltypes)) / n_methods,
            index=methods,
            columns=cell_types,
        )
        return row_normalize(pd.DataFrame(pred, index=spots, columns=cell_types)), W, [W]

    folds = make_folds(n_spots, n_folds=n_folds, seed=seed)
    out = np.zeros((n_spots, n_celltypes), dtype=float)
    weight_folds = []

    for fold_id, test_idx in enumerate(folds, start=1):
        train_mask = np.ones(n_spots, dtype=bool)
        train_mask[test_idx] = False
        train_idx = np.where(train_mask)[0]

        W = np.zeros((n_methods, n_celltypes), dtype=float)

        if strategy == "GlobalInvRMSE":
            rmses = []
            for mi in range(n_methods):
                pred_train = arr[mi, train_idx, :]
                true_train = y[train_idx, :]
                rmse = np.sqrt(np.mean((pred_train - true_train) ** 2))
                rmses.append(rmse)

            inv = 1.0 / (np.asarray(rmses) + 1e-8)
            if inv.sum() <= 0 or not np.all(np.isfinite(inv)):
                gw = np.ones(n_methods) / n_methods
            else:
                gw = inv / inv.sum()

            for ci in range(n_celltypes):
                W[:, ci] = gw

        elif strategy == "CellTypeHardSelect":
            for ci in range(n_celltypes):
                rmses = []
                for mi in range(n_methods):
                    rmse = np.sqrt(np.mean((arr[mi, train_idx, ci] - y[train_idx, ci]) ** 2))
                    rmses.append(rmse)
                best = int(np.argmin(rmses))
                W[best, ci] = 1.0

        elif strategy == "CellTypeInvRMSE":
            for ci in range(n_celltypes):
                rmses = []
                for mi in range(n_methods):
                    rmse = np.sqrt(np.mean((arr[mi, train_idx, ci] - y[train_idx, ci]) ** 2))
                    rmses.append(rmse)
                inv = 1.0 / (np.asarray(rmses) + 1e-8)
                if inv.sum() <= 0 or not np.all(np.isfinite(inv)):
                    W[:, ci] = np.ones(n_methods) / n_methods
                else:
                    W[:, ci] = inv / inv.sum()

        elif strategy == "CTW-RF":
            for ci in range(n_celltypes):
                X_train = arr[:, train_idx, ci].T
                y_train = y[train_idx, ci]
                W[:, ci] = solve_simplex_weights(X_train, y_train)

        else:
            raise ValueError("Unknown strategy: " + strategy)

        for ci in range(n_celltypes):
            out[test_idx, ci] = arr[:, test_idx, ci].T @ W[:, ci]

        W_df = pd.DataFrame(W, index=methods, columns=cell_types)
        weight_folds.append(W_df)
        print(f"[{strategy}] fold {fold_id}/{n_folds} done")

    avg_W = sum(weight_folds) / len(weight_folds)
    pred_df = row_normalize(pd.DataFrame(out, index=spots, columns=cell_types))
    return pred_df, avg_W, weight_folds


def best_single_baseline(preds, methods, gt):
    records = []
    for m in methods:
        records.append(evaluate_prediction(m, preds[m], gt))
    table = pd.DataFrame(records).set_index("method")
    best = table.sort_values("aggregated_celltype_RMSE", ascending=True).index[0]
    return best, table


# ============================================================
# 6. Ablation
# ============================================================
def run_ablation(preds, gt):
    print("\n" + "=" * 70)
    print("A. Fusion strategy ablation")
    print("=" * 70)

    available_core = [m for m in CORE_METHODS if m in preds]
    available_ext = [m for m in EXTENDED_METHODS if m in preds]

    print("[core methods]", available_core)
    print("[extended methods]", available_ext)

    best_name, baseline_table = best_single_baseline(preds, available_ext, gt)
    print("[Best single by aggregated RMSE]", best_name)

    fusion_outputs = {}
    fusion_outputs["BestSingle"] = preds[best_name].loc[gt.index, gt.columns].copy()

    core_strategies = [
        "SimpleAverage",
        "GlobalInvRMSE",
        "CellTypeHardSelect",
        "CellTypeInvRMSE",
        "CTW-RF",
    ]

    for strategy in core_strategies:
        pred, W, W_folds = fit_cv_fusion(preds, available_core, gt, strategy=strategy)
        fusion_outputs[strategy] = pred
        pred.to_csv(os.path.join(PRED_OUT_DIR, f"{strategy}_core_pool_prediction.csv"))
        W.to_csv(os.path.join(WEIGHT_OUT_DIR, f"{strategy}_core_pool_weights.csv"))

    ext_pred, ext_W, ext_W_folds = fit_cv_fusion(preds, available_ext, gt, strategy="CTW-RF")
    fusion_outputs["CTW-RF+SpaDAMA+SpaJoint"] = ext_pred
    ext_pred.to_csv(os.path.join(PRED_OUT_DIR, "CTW_RF_extended_SpaDAMA_SpaJoint_prediction.csv"))
    ext_W.to_csv(os.path.join(WEIGHT_OUT_DIR, "CTW_RF_extended_SpaDAMA_SpaJoint_weights.csv"))

    records = []
    for name, pred in fusion_outputs.items():
        records.append(evaluate_prediction(name, pred, gt))

    ablation = pd.DataFrame(records).set_index("method")
    ablation["note"] = ""
    ablation.loc["BestSingle", "note"] = f"best single = {best_name}"

    ablation["JSD_rank"] = ablation["JSD"].rank(method="min", ascending=True).astype(int)
    ablation["aggregated_RMSE_rank"] = ablation["aggregated_celltype_RMSE"].rank(method="min", ascending=True).astype(int)
    ablation["mean_rank"] = ablation[["JSD_rank", "aggregated_RMSE_rank"]].mean(axis=1)

    order = [
        "BestSingle",
        "SimpleAverage",
        "GlobalInvRMSE",
        "CellTypeHardSelect",
        "CellTypeInvRMSE",
        "CTW-RF",
        "CTW-RF+SpaDAMA+SpaJoint",
    ]
    ablation = ablation.loc[[x for x in order if x in ablation.index]]

    ablation.to_csv(os.path.join(OUT_DIR, "Table2_ablation_fusion_strategies.csv"))
    baseline_table.to_csv(os.path.join(OUT_DIR, "single_baseline_metrics_for_ablation.csv"))

    print("\n[Ablation table]")
    show_cols = ["JSD", "matrix_RMSE", "aggregated_celltype_RMSE", "mean_celltype_RMSE", "JSD_rank", "aggregated_RMSE_rank", "mean_rank", "note"]
    print(ablation[show_cols])

    return ablation, baseline_table, ext_W


# ============================================================
# 7. Robustness
# ============================================================
def run_robustness(preds, gt):
    print("\n" + "=" * 70)
    print("B. Candidate-pool robustness / leave-one-method-out")
    print("=" * 70)

    available_ext = [m for m in EXTENDED_METHODS if m in preds]
    records = []

    settings = [("FullPool", available_ext)]
    for m in available_ext:
        methods = [x for x in available_ext if x != m]
        settings.append((f"without_{m}", methods))

    for setting_name, methods in settings:
        print("\n[Robustness]", setting_name, "methods:", methods)
        pred, W, W_folds = fit_cv_fusion(preds, methods, gt, strategy="CTW-RF")
        pred.to_csv(os.path.join(PRED_OUT_DIR, f"robustness_{setting_name}_prediction.csv"))
        W.to_csv(os.path.join(WEIGHT_OUT_DIR, f"robustness_{setting_name}_weights.csv"))

        rec = evaluate_prediction(setting_name, pred, gt)
        rec["removed_method"] = "" if setting_name == "FullPool" else setting_name.replace("without_", "")
        rec["candidate_pool_size"] = len(methods)
        records.append(rec)

    robustness = pd.DataFrame(records).set_index("method")
    robustness["delta_RMSE_vs_full"] = robustness["aggregated_celltype_RMSE"] - robustness.loc["FullPool", "aggregated_celltype_RMSE"]
    robustness["delta_JSD_vs_full"] = robustness["JSD"] - robustness.loc["FullPool", "JSD"]

    robustness.to_csv(os.path.join(OUT_DIR, "Table3_candidate_pool_robustness.csv"))

    show_cols = [
        "removed_method",
        "candidate_pool_size",
        "JSD",
        "aggregated_celltype_RMSE",
        "mean_celltype_RMSE",
        "delta_RMSE_vs_full",
        "delta_JSD_vs_full",
    ]
    print("\n[Robustness table]")
    print(robustness[show_cols])

    return robustness


# ============================================================
# 8. Plotting
# ============================================================
def savefig(name):
    png = os.path.join(FIG_DIR, name + ".png")
    pdf = os.path.join(FIG_DIR, name + ".pdf")
    svg = os.path.join(FIG_DIR, name + ".svg")
    plt.tight_layout()
    plt.savefig(png, dpi=300, bbox_inches="tight")
    plt.savefig(pdf, bbox_inches="tight")
    plt.savefig(svg, bbox_inches="tight")
    plt.close()
    print("saved:", png)
    print("saved:", pdf)
    print("saved:", svg)


def plot_ablation(ablation):
    df = ablation.copy().sort_values("aggregated_celltype_RMSE", ascending=True)
    methods = list(df.index)
    x = np.arange(len(methods))

    plt.figure(figsize=(10.5, 5.2))
    bars = plt.bar(
        x,
        df["aggregated_celltype_RMSE"].values,
        color=[color_for(m) for m in methods],
        edgecolor="black",
        linewidth=0.5,
    )
    plt.xticks(x, [display(m) for m in methods], rotation=30, ha="right")
    plt.ylabel("Aggregated cell-type RMSE (lower is better)")
    plt.title("Ablation study of fusion strategies")
    plt.grid(axis="y", alpha=0.25)

    ymax = df["aggregated_celltype_RMSE"].max()
    for b, v in zip(bars, df["aggregated_celltype_RMSE"].values):
        plt.text(b.get_x() + b.get_width() / 2, v + ymax * 0.01, f"{v:.3f}",
                 ha="center", va="bottom", fontsize=9)
    savefig("Figure9_ablation_aggregated_RMSE")

    df2 = ablation.copy().sort_values("JSD", ascending=True)
    methods = list(df2.index)
    x = np.arange(len(methods))

    plt.figure(figsize=(10.5, 5.2))
    bars = plt.bar(
        x,
        df2["JSD"].values,
        color=[color_for(m) for m in methods],
        edgecolor="black",
        linewidth=0.5,
    )
    plt.xticks(x, [display(m) for m in methods], rotation=30, ha="right")
    plt.ylabel("JSD (lower is better)")
    plt.title("Ablation study of fusion strategies: JSD")
    plt.grid(axis="y", alpha=0.25)

    ymax = df2["JSD"].max()
    for b, v in zip(bars, df2["JSD"].values):
        plt.text(b.get_x() + b.get_width() / 2, v + ymax * 0.01, f"{v:.3f}",
                 ha="center", va="bottom", fontsize=9)
    savefig("Figure9_ablation_JSD")


def plot_robustness(robustness):
    df = robustness.copy()
    plot_names = []
    for idx, row in df.iterrows():
        if idx == "FullPool":
            plot_names.append("Full pool")
        else:
            plot_names.append("w/o " + str(row["removed_method"]))

    df["plot_name"] = plot_names
    df_sorted = df.sort_values("aggregated_celltype_RMSE", ascending=True)
    x = np.arange(len(df_sorted))

    plt.figure(figsize=(11.5, 5.2))
    colors = ["#C7354A" if idx == "FullPool" else "#C5CBD3" for idx in df_sorted.index]
    bars = plt.bar(
        x,
        df_sorted["aggregated_celltype_RMSE"].values,
        color=colors,
        edgecolor="black",
        linewidth=0.5,
    )
    plt.xticks(x, df_sorted["plot_name"].values, rotation=30, ha="right")
    plt.ylabel("Aggregated cell-type RMSE (lower is better)")
    plt.title("Candidate-pool robustness analysis")
    plt.grid(axis="y", alpha=0.25)

    ymax = df_sorted["aggregated_celltype_RMSE"].max()
    for b, v in zip(bars, df_sorted["aggregated_celltype_RMSE"].values):
        plt.text(b.get_x() + b.get_width() / 2, v + ymax * 0.01, f"{v:.3f}",
                 ha="center", va="bottom", fontsize=9)
    savefig("Figure10_candidate_pool_robustness_RMSE")

    df_delta = df.loc[[idx for idx in df.index if idx != "FullPool"]].copy()
    df_delta = df_delta.sort_values("delta_RMSE_vs_full", ascending=False)
    x = np.arange(len(df_delta))

    plt.figure(figsize=(11.5, 5.2))
    bars = plt.bar(
        x,
        df_delta["delta_RMSE_vs_full"].values,
        color="#C5CBD3",
        edgecolor="black",
        linewidth=0.5,
    )
    plt.axhline(0, color="black", linewidth=0.8)
    plt.xticks(x, ["w/o " + str(m) for m in df_delta["removed_method"].values], rotation=30, ha="right")
    plt.ylabel("Delta aggregated RMSE vs full pool")
    plt.title("Effect of removing each candidate method")
    plt.grid(axis="y", alpha=0.25)

    max_abs = max(abs(df_delta["delta_RMSE_vs_full"].min()), abs(df_delta["delta_RMSE_vs_full"].max()))
    offset = max_abs * 0.03 if max_abs > 0 else 0.001
    for b, v in zip(bars, df_delta["delta_RMSE_vs_full"].values):
        va = "bottom" if v >= 0 else "top"
        y = v + offset if v >= 0 else v - offset
        plt.text(b.get_x() + b.get_width() / 2, y, f"{v:+.3f}",
                 ha="center", va=va, fontsize=9)
    savefig("Figure10_candidate_pool_robustness_delta_RMSE")


def plot_weight_heatmap(ext_W):
    W = ext_W.copy()
    order = [m for m in EXTENDED_METHODS if m in W.index]
    W = W.loc[order]

    plt.figure(figsize=(max(9, W.shape[1] * 0.6), max(4.8, W.shape[0] * 0.42)))
    im = plt.imshow(W.values, aspect="auto", vmin=0, vmax=max(1.0, float(np.nanmax(W.values))))
    plt.yticks(range(W.shape[0]), [display(m) for m in W.index])
    plt.xticks(range(W.shape[1]), W.columns, rotation=45, ha="right")
    plt.title("CTW-RF extended candidate pool: fusion weights")
    plt.colorbar(im, label="Weight")
    savefig("Figure11_extended_pool_weight_heatmap")

    contrib = W.sum(axis=1).sort_values(ascending=False)
    contrib.to_csv(os.path.join(OUT_DIR, "extended_pool_method_weight_contribution.csv"))

    plt.figure(figsize=(8.5, 4.8))
    x = np.arange(len(contrib))
    bars = plt.bar(
        x,
        contrib.values,
        color=[color_for(m) for m in contrib.index],
        edgecolor="black",
        linewidth=0.5,
    )
    plt.xticks(x, [display(m) for m in contrib.index], rotation=30, ha="right")
    plt.ylabel("Sum of weights across cell types")
    plt.title("Contribution of candidate methods in extended CTW-RF")
    plt.grid(axis="y", alpha=0.25)

    ymax = contrib.max()
    for b, v in zip(bars, contrib.values):
        plt.text(b.get_x() + b.get_width() / 2, v + ymax * 0.01, f"{v:.2f}",
                 ha="center", va="bottom", fontsize=9)
    savefig("Figure11_extended_pool_method_contribution")


# ============================================================
# 9. Main
# ============================================================
def main():
    print("=" * 70)
    print("CTW-RF ablation and robustness analysis")
    print("=" * 70)
    print("BASE_DIR:", BASE_DIR)
    print("PRED_DIR:", PRED_DIR)
    print("OUT_DIR:", OUT_DIR)

    gt = read_matrix(GT_PATH)
    gt = row_normalize(gt)
    gt.index = gt.index.astype(str)
    gt.columns = gt.columns.astype(str)

    print("[GT]", gt.shape)
    print("[GT cols]", list(gt.columns))

    preds, reports = load_predictions(gt)

    missing_core = [m for m in CORE_METHODS if m not in preds]
    missing_ext = [m for m in EXTENDED_METHODS if m not in preds]
    if missing_core:
        raise RuntimeError("Missing core method predictions: " + str(missing_core))
    if missing_ext:
        print("[WARN] Missing extended methods:", missing_ext)
        print("The script will continue with available methods.")

    ablation, baseline_table, ext_W = run_ablation(preds, gt)
    robustness = run_robustness(preds, gt)

    print("\n" + "=" * 70)
    print("Plotting")
    print("=" * 70)

    plot_ablation(ablation)
    plot_robustness(robustness)
    plot_weight_heatmap(ext_W)

    print("\nDONE")
    print("Tables saved to:", OUT_DIR)
    print("Figures saved to:", FIG_DIR)
    print("Predictions saved to:", PRED_OUT_DIR)
    print("Weights saved to:", WEIGHT_OUT_DIR)


if __name__ == "__main__":
    main()
