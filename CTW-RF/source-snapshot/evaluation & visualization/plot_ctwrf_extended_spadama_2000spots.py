# -*- coding: utf-8 -*-
"""
Plot paper-style figures for SpaDAMA + CTW-RF-extended benchmark on
self_benchmark_cortex_svz_2000spots.

What this script does
---------------------
1. Read the evaluation outputs produced by:
   evaluate_spadama_ctwrf_extended_2000spots.py
2. Generate several standalone figures:
   - JSD barplot
   - Aggregated cell-type RMSE barplot
   - JSD vs aggregated RMSE scatter plot
   - Per-cell-type RMSE heatmap
   - Average fusion weight heatmap
   - Winner-count barplot (which method is best on each cell type)
3. Generate one integrated multi-panel figure for paper / PPT use.

Recommended run
---------------
python "D:/Research/STdeconv_benchmark/evaluation & visualization/plot_ctwrf_extended_spadama_2000spots.py"

Dependencies
------------
- numpy
- pandas
- matplotlib
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. User paths
# ============================================================
BASE_DIR = r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots"
PRED_DIR = os.path.join(BASE_DIR, "predictions")
GT_PATH = os.path.join(BASE_DIR, "pseudo_spot_ground_truth.csv")

EVAL_DIR = r"D:\Research\STdeconv_benchmark\evaluation & visualization\ctwrf_extended_spadama_2000spots"
OUT_DIR = os.path.join(EVAL_DIR, "paper_figures")
os.makedirs(OUT_DIR, exist_ok=True)

METRICS_PATH = os.path.join(EVAL_DIR, "01_metrics_all_methods_with_spadama.csv")
COMPARISON_PATH = os.path.join(EVAL_DIR, "02_main_comparison_with_spadama.csv")
WEIGHT_PATH = os.path.join(EVAL_DIR, "weights_CTW_RF_extended_SpaDAMA_average.csv")
TABLE_PATH = os.path.join(EVAL_DIR, "Table1_with_SpaDAMA_and_CTWRF_extended.csv")


# ============================================================
# 2. Basic utilities
# ============================================================
EPS = 1e-12


BASELINE_FILES = {
    "Tangram": "Tangram_self_benchmark.csv",
    "RCTD": "RCTD_self_benchmark.csv",
    "CellDART": "CellDART_self_benchmark.csv",
    "CARD": "CARD_self_benchmark.csv",
    "cell2location": "Cell2location_self_benchmark.csv",
    "SPOTlight": "SPOTlight_self_benchmark.csv",
    "SpaDAMA": "SpaDAMA_self_benchmark.csv",
    "CTW-RF": "Proposed_CV_best_self_benchmark.csv",
    "CTW-RF+SpaDAMA": "CTW_RF_extended_SpaDAMA_self_benchmark.csv",
}


def read_matrix(path: str) -> pd.DataFrame:
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
    common_spots = gt.index.intersection(pred.index)
    if len(common_spots) == 0:
        raise ValueError("No common spots between pred and gt")

    pred = pred.loc[common_spots].copy()
    gt_use = gt.loc[common_spots].copy()

    aligned = pd.DataFrame(0.0, index=gt_use.index, columns=gt_use.columns)
    common_cols = [c for c in gt_use.columns if c in pred.columns]
    aligned.loc[:, common_cols] = pred.loc[:, common_cols].values
    return row_normalize(aligned)


def per_celltype_rmse(pred: pd.DataFrame, gt: pd.DataFrame) -> pd.Series:
    vals = {}
    for c in gt.columns:
        vals[c] = float(np.sqrt(np.mean((pred[c].values - gt[c].values) ** 2)))
    return pd.Series(vals)


def method_color(name: str) -> str:
    if name == "CTW-RF+SpaDAMA":
        return "#C8374A"  # red highlight
    if name == "SpaDAMA":
        return "#E68632"  # orange highlight
    if name == "CTW-RF":
        return "#6C8EBF"  # blue for previous fusion
    return "#BFC5CE"      # gray baseline


# ============================================================
# 3. Load metrics / predictions
# ============================================================
def load_all():
    if not os.path.exists(COMPARISON_PATH):
        raise FileNotFoundError(COMPARISON_PATH)

    gt = row_normalize(read_matrix(GT_PATH))
    metrics = pd.read_csv(METRICS_PATH, index_col=0)
    comparison = pd.read_csv(COMPARISON_PATH, index_col=0)
    weights = pd.read_csv(WEIGHT_PATH, index_col=0)

    pred_dict = {}
    for name, fname in BASELINE_FILES.items():
        path = os.path.join(PRED_DIR, fname)
        if os.path.exists(path):
            pred_dict[name] = align_prediction(read_matrix(path), gt)

    return gt, metrics, comparison, weights, pred_dict


# ============================================================
# 4. Individual plots
# ============================================================
def plot_bar(df: pd.DataFrame, value_col: str, title: str, ylabel: str, out_path: str):
    plot_df = df.sort_values(value_col, ascending=True)
    methods = plot_df.index.tolist()
    values = plot_df[value_col].values
    colors = [method_color(m) for m in methods]

    plt.figure(figsize=(8.5, 4.8))
    x = np.arange(len(methods))
    bars = plt.bar(x, values, color=colors, edgecolor="black", linewidth=0.5)
    plt.xticks(x, methods, rotation=35, ha="right")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(axis="y", alpha=0.25)

    offset = max(values) * 0.015 if len(values) > 0 else 0.01
    for bar, v in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, v + offset, f"{v:.3f}",
                 ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_scatter(df: pd.DataFrame, out_path: str):
    plot_df = df.copy()

    plt.figure(figsize=(6.4, 5.2))
    for method, row in plot_df.iterrows():
        if method == "CTW-RF+SpaDAMA":
            size = 110
        elif method in ["SpaDAMA", "CTW-RF"]:
            size = 80
        else:
            size = 60
        plt.scatter(row["JSD"], row["aggregated_celltype_RMSE"],
                    s=size, color=method_color(method), edgecolor="black", linewidth=0.5)
        plt.text(row["JSD"] + 0.002, row["aggregated_celltype_RMSE"], method,
                 fontsize=9, va="center")

    plt.xlabel("JSD (lower is better)")
    plt.ylabel("Aggregated cell-type RMSE (lower is better)")
    plt.title("Performance trade-off")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_celltype_rmse_heatmap(gt: pd.DataFrame, pred_dict: dict, method_order: list, out_path: str):
    heat = []
    used_methods = []
    for m in method_order:
        if m in pred_dict:
            heat.append(per_celltype_rmse(pred_dict[m], gt).values)
            used_methods.append(m)
    heat = np.asarray(heat)
    celltypes = gt.columns.tolist()

    plt.figure(figsize=(12, 4.8))
    im = plt.imshow(heat, aspect="auto")
    plt.yticks(np.arange(len(used_methods)), used_methods)
    plt.xticks(np.arange(len(celltypes)), celltypes, rotation=45, ha="right")
    plt.title("Cell-type RMSE heatmap")
    cbar = plt.colorbar(im)
    cbar.set_label("RMSE")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_weight_heatmap(weights: pd.DataFrame, out_path: str):
    arr = weights.values
    methods = weights.index.tolist()
    celltypes = weights.columns.tolist()

    plt.figure(figsize=(12, 4.2))
    im = plt.imshow(arr, aspect="auto", vmin=0, vmax=max(1.0, float(np.nanmax(arr))))
    plt.yticks(np.arange(len(methods)), methods)
    plt.xticks(np.arange(len(celltypes)), celltypes, rotation=45, ha="right")
    plt.title("Average cell-type-wise fusion weights")
    cbar = plt.colorbar(im)
    cbar.set_label("Weight")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_winner_count(gt: pd.DataFrame, pred_dict: dict, method_order: list, out_path: str):
    rmse_map = {}
    for m in method_order:
        if m in pred_dict:
            rmse_map[m] = per_celltype_rmse(pred_dict[m], gt)

    rmse_df = pd.DataFrame(rmse_map)
    winners = rmse_df.idxmin(axis=1)
    counts = winners.value_counts().reindex([m for m in method_order if m in rmse_df.columns], fill_value=0)

    plt.figure(figsize=(8.0, 4.4))
    x = np.arange(len(counts))
    colors = [method_color(m) for m in counts.index]
    bars = plt.bar(x, counts.values, color=colors, edgecolor="black", linewidth=0.5)
    plt.xticks(x, counts.index, rotation=35, ha="right")
    plt.ylabel("Number of best cell types")
    plt.title("Winner count across cell types")
    plt.grid(axis="y", alpha=0.25)
    for b, v in zip(bars, counts.values):
        plt.text(b.get_x() + b.get_width() / 2, v + 0.05, str(int(v)), ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


# ============================================================
# 5. Integrated paper figure
# ============================================================
def plot_main_figure(gt: pd.DataFrame, comparison: pd.DataFrame, weights: pd.DataFrame, pred_dict: dict, out_path: str):
    method_order = [m for m in [
        "Tangram", "RCTD", "CellDART", "CARD", "cell2location", "SPOTlight", "SpaDAMA", "CTW-RF", "CTW-RF+SpaDAMA"
    ] if m in comparison.index]

    rmse_heat = []
    used_methods = []
    for m in method_order:
        if m in pred_dict:
            rmse_heat.append(per_celltype_rmse(pred_dict[m], gt).values)
            used_methods.append(m)
    rmse_heat = np.asarray(rmse_heat)
    celltypes = gt.columns.tolist()

    rmse_df = pd.DataFrame({m: per_celltype_rmse(pred_dict[m], gt) for m in used_methods})
    winner_counts = rmse_df.idxmin(axis=1).value_counts().reindex(used_methods, fill_value=0)

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle("Benchmark performance after adding SpaDAMA", fontsize=18, y=0.98)

    # A
    ax1 = plt.subplot2grid((3, 3), (0, 0))
    plot_df = comparison.loc[method_order].sort_values("JSD")
    x = np.arange(len(plot_df))
    ax1.bar(x, plot_df["JSD"].values, color=[method_color(m) for m in plot_df.index], edgecolor="black", linewidth=0.4)
    ax1.set_xticks(x)
    ax1.set_xticklabels(plot_df.index, rotation=35, ha="right", fontsize=9)
    ax1.set_ylabel("JSD")
    ax1.set_title("A  Distributional similarity")
    ax1.grid(axis="y", alpha=0.25)

    # B
    ax2 = plt.subplot2grid((3, 3), (0, 1))
    plot_df2 = comparison.loc[method_order].sort_values("aggregated_celltype_RMSE")
    x2 = np.arange(len(plot_df2))
    ax2.bar(x2, plot_df2["aggregated_celltype_RMSE"].values,
            color=[method_color(m) for m in plot_df2.index], edgecolor="black", linewidth=0.4)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(plot_df2.index, rotation=35, ha="right", fontsize=9)
    ax2.set_ylabel("Aggregated RMSE")
    ax2.set_title("B  Cell-type-level accuracy")
    ax2.grid(axis="y", alpha=0.25)

    # C
    ax3 = plt.subplot2grid((3, 3), (0, 2))
    for m in method_order:
        row = comparison.loc[m]
        ax3.scatter(row["JSD"], row["aggregated_celltype_RMSE"],
                    s=110 if m == "CTW-RF+SpaDAMA" else (80 if m in ["SpaDAMA", "CTW-RF"] else 60),
                    color=method_color(m), edgecolor="black", linewidth=0.4)
        ax3.text(row["JSD"] + 0.002, row["aggregated_celltype_RMSE"], m, fontsize=8, va="center")
    ax3.set_xlabel("JSD")
    ax3.set_ylabel("Aggregated RMSE")
    ax3.set_title("C  Performance trade-off")
    ax3.grid(alpha=0.25)

    # D
    ax4 = plt.subplot2grid((3, 3), (1, 0), colspan=3)
    im4 = ax4.imshow(rmse_heat, aspect="auto")
    ax4.set_yticks(np.arange(len(used_methods)))
    ax4.set_yticklabels(used_methods)
    ax4.set_xticks(np.arange(len(celltypes)))
    ax4.set_xticklabels(celltypes, rotation=45, ha="right")
    ax4.set_title("D  Cell-type RMSE heatmap")
    cbar4 = plt.colorbar(im4, ax=ax4, fraction=0.02, pad=0.02)
    cbar4.set_label("RMSE")

    # E
    ax5 = plt.subplot2grid((3, 3), (2, 0), colspan=2)
    im5 = ax5.imshow(weights.values, aspect="auto", vmin=0, vmax=max(1.0, float(np.nanmax(weights.values))))
    ax5.set_yticks(np.arange(len(weights.index)))
    ax5.set_yticklabels(weights.index)
    ax5.set_xticks(np.arange(len(weights.columns)))
    ax5.set_xticklabels(weights.columns, rotation=45, ha="right")
    ax5.set_title("E  Average fusion weights")
    cbar5 = plt.colorbar(im5, ax=ax5, fraction=0.03, pad=0.02)
    cbar5.set_label("Weight")

    # F
    ax6 = plt.subplot2grid((3, 3), (2, 2))
    xx = np.arange(len(winner_counts))
    ax6.bar(xx, winner_counts.values, color=[method_color(m) for m in winner_counts.index], edgecolor="black", linewidth=0.4)
    ax6.set_xticks(xx)
    ax6.set_xticklabels(winner_counts.index, rotation=35, ha="right", fontsize=9)
    ax6.set_ylabel("Best cell types")
    ax6.set_title("F  Winner count")
    ax6.grid(axis="y", alpha=0.25)

    plt.tight_layout(rect=[0, 0, 1, 0.965])
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


# ============================================================
# 6. Main
# ============================================================
def main():
    print("=" * 60)
    print("Plot SpaDAMA + CTW-RF-extended figures")
    print("=" * 60)
    print("EVAL_DIR:", EVAL_DIR)
    print("OUT_DIR:", OUT_DIR)

    gt, metrics, comparison, weights, pred_dict = load_all()

    method_order = [m for m in [
        "Tangram", "RCTD", "CellDART", "CARD", "cell2location", "SPOTlight", "SpaDAMA", "CTW-RF", "CTW-RF+SpaDAMA"
    ] if m in comparison.index]

    compact = comparison.loc[method_order, [
        "JSD", "matrix_RMSE", "aggregated_celltype_RMSE", "mean_celltype_RMSE", "JSD_rank", "aggregated_RMSE_rank", "mean_rank"
    ]]
    compact.to_csv(os.path.join(OUT_DIR, "Table_for_plotting.csv"))

    plot_bar(comparison.loc[method_order], "JSD", "JSD comparison", "JSD (lower is better)",
             os.path.join(OUT_DIR, "01_JSD_barplot.png"))

    plot_bar(comparison.loc[method_order], "aggregated_celltype_RMSE", "Aggregated cell-type RMSE comparison",
             "Aggregated cell-type RMSE (lower is better)",
             os.path.join(OUT_DIR, "02_aggregated_RMSE_barplot.png"))

    plot_scatter(comparison.loc[method_order], os.path.join(OUT_DIR, "03_tradeoff_scatter.png"))

    plot_celltype_rmse_heatmap(gt, pred_dict, method_order,
                               os.path.join(OUT_DIR, "04_celltype_RMSE_heatmap.png"))

    plot_weight_heatmap(weights, os.path.join(OUT_DIR, "05_average_weight_heatmap.png"))

    plot_winner_count(gt, pred_dict, method_order,
                      os.path.join(OUT_DIR, "06_winner_count.png"))

    plot_main_figure(gt, comparison, weights, pred_dict,
                     os.path.join(OUT_DIR, "Figure_main_SpaDAMA_CTW_RF_extended.png"))

    print("Saved figures to:")
    print(OUT_DIR)
    print("DONE")


if __name__ == "__main__":
    main()