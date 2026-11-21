# -*- coding: utf-8 -*-
"""
Paper-style plotting script for CTW-RF on self_benchmark_cortex_svz_2000spots.

Purpose
-------
This script reads the 5-fold CV verification outputs and produces a clean,
paper-ready multi-panel figure and quantitative table.

Recommended order:
1) Run verify_cv_reliability_fusion_2000spots.py
2) Run this script

Main outputs
------------
- Figure2_CTW_RF_benchmark.png
- Figure2_CTW_RF_benchmark.pdf
- Figure2_CTW_RF_benchmark.svg
- Table1_CTW_RF_metrics.csv
- CTW_RF_result_summary.txt

Default input directory
-----------------------
D:/Research/STdeconv_benchmark/evaluation & visualization/reliability_fusion_2000spots_cv_verify
"""

import os
import re
import textwrap
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.colors import LinearSegmentedColormap


# ============================================================
# 1. Paths
# ============================================================
CV_EVAL_DIR = r"D:\Research\STdeconv_benchmark\evaluation & visualization\reliability_fusion_2000spots_cv_verify"

METRICS_CSV = os.path.join(CV_EVAL_DIR, "03_main_cv_comparison.csv")
ALL_METRICS_CSV = os.path.join(CV_EVAL_DIR, "01_metrics_all_methods.csv")
WEIGHTS_CSV = os.path.join(CV_EVAL_DIR, "weights_Proposed_CV_best.csv")
WINNER_CSV = os.path.join(CV_EVAL_DIR, "05_cv_celltype_winner_count.csv")
IMPROVE_CSV = os.path.join(CV_EVAL_DIR, "04_main_cv_improvement_vs_best_baseline.csv")

OUT_DIR = r"D:\Research\STdeconv_benchmark\evaluation & visualization\paper_figures_CTW_RF_2000spots"
os.makedirs(OUT_DIR, exist_ok=True)


# ============================================================
# 2. Display settings
# ============================================================
METHOD_ORDER = [
    "Tangram",
    "RCTD",
    "CellDART",
    "CARD",
    "cell2location",
    "SPOTlight",
    "CTW-RF",
]

RENAME_MAP = {
    "Proposed_CV": "CTW-RF",
    "Proposed": "CTW-RF",
    "Proposed_CV_best": "CTW-RF",
}

DISPLAY_NAME = {
    "Tangram": "Tangram",
    "RCTD": "RCTD",
    "CellDART": "CellDART",
    "CARD": "CARD",
    "cell2location": "cell2location",
    "SPOTlight": "SPOTlight",
    "CTW-RF": "CTW-RF",
}

BASELINE_COLOR = "#B8BEC9"
CTWRF_COLOR = "#C83E4D"

METHOD_COLORS = {
    "Tangram": "#B8BEC9",
    "RCTD": "#B8BEC9",
    "CellDART": "#B8BEC9",
    "CARD": "#B8BEC9",
    "cell2location": "#B8BEC9",
    "SPOTlight": "#B8BEC9",
    "CTW-RF": CTWRF_COLOR,
}

# Soft scientific colormap for heatmaps.
HEAT_CMAP = LinearSegmentedColormap.from_list(
    "ctwrf_heat",
    ["#F9FBFD", "#DBE7F3", "#94B9D8", "#3F7CAC", "#173F5F"]
)

WEIGHT_CMAP = LinearSegmentedColormap.from_list(
    "ctwrf_weight",
    ["#F7FBFF", "#CFE8F3", "#7CC6C2", "#2A9D8F", "#0B6E4F"]
)


# ============================================================
# 3. Utility functions
# ============================================================
def read_csv_smart(path: str, index_col=0) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    try:
        return pd.read_csv(path, index_col=index_col, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, index_col=index_col)


def normalize_method_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.index = [RENAME_MAP.get(str(x), str(x)) for x in df.index]
    return df


def infer_celltype_columns(df: pd.DataFrame) -> List[str]:
    metric_cols = {
        "JSD",
        "matrix_RMSE",
        "total_RMSE",
        "aggregated_celltype_RMSE",
        "mean_celltype_RMSE",
        "JSD_rank",
        "RMSE_rank",
        "mean_rank",
        "display_name",
        "source_file",
        "method_group",
    }

    celltype_cols = []
    for c in df.columns:
        cs = str(c)
        if cs in metric_cols:
            continue
        # This benchmark uses labels like L10, L11, L2, L23...
        if re.match(r"^L[0-9]+$", cs):
            celltype_cols.append(cs)

    if not celltype_cols:
        # Fallback: all numeric columns except known global metric columns.
        for c in df.columns:
            if c not in metric_cols and pd.api.types.is_numeric_dtype(df[c]):
                celltype_cols.append(c)

    # Natural sorting: L2 before L10
    def ct_key(x):
        m = re.match(r"^L(\d+)$", str(x))
        return int(m.group(1)) if m else 9999

    return sorted(celltype_cols, key=ct_key)


def order_methods(df: pd.DataFrame) -> pd.DataFrame:
    available = [m for m in METHOD_ORDER if m in df.index]
    others = [m for m in df.index if m not in available]
    return df.loc[available + others].copy()


def set_paper_style():
    plt.rcParams.update({
        "font.family": "Arial",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.titlesize": 12,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.bbox": "tight",
    })


def add_panel_label(ax, label: str):
    ax.text(
        -0.12, 1.08, label,
        transform=ax.transAxes,
        fontsize=13,
        fontweight="bold",
        va="top",
        ha="left",
    )


def barplot_metric(ax, df: pd.DataFrame, col: str, ylabel: str, title: str, panel_label: str):
    values = df[col].astype(float)
    x = np.arange(len(values))
    colors = [METHOD_COLORS.get(m, BASELINE_COLOR) for m in values.index]

    ax.bar(x, values.values, color=colors, edgecolor="white", linewidth=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([DISPLAY_NAME.get(m, m) for m in values.index], rotation=35, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=8)
    ax.grid(axis="y", alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)

    # Annotate values.
    ylim = ax.get_ylim()
    offset = (ylim[1] - ylim[0]) * 0.015
    for i, v in enumerate(values.values):
        ax.text(i, v + offset, f"{v:.3f}", ha="center", va="bottom", fontsize=7.5)

    # Highlight best.
    best_idx = int(np.nanargmin(values.values))
    ax.scatter([best_idx], [values.values[best_idx]], s=28, color="#222222", zorder=5)

    add_panel_label(ax, panel_label)


def scatter_tradeoff(ax, df: pd.DataFrame):
    for method, row in df.iterrows():
        color = METHOD_COLORS.get(method, BASELINE_COLOR)
        size = 95 if method == "CTW-RF" else 55
        edge = "#222222" if method == "CTW-RF" else "white"
        lw = 0.8 if method == "CTW-RF" else 0.5

        ax.scatter(
            row["JSD"],
            row["aggregated_celltype_RMSE"],
            s=size,
            color=color,
            edgecolor=edge,
            linewidth=lw,
            zorder=4 if method == "CTW-RF" else 3,
        )
        ax.text(
            row["JSD"],
            row["aggregated_celltype_RMSE"],
            "  " + DISPLAY_NAME.get(method, method),
            va="center",
            fontsize=8,
        )

    ax.set_xlabel("JSD (lower is better)")
    ax.set_ylabel("Aggregated cell-type RMSE\n(lower is better)")
    ax.set_title("Performance trade-off", pad=8)
    ax.grid(alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    add_panel_label(ax, "C")


def heatmap_celltype_rmse(ax, df: pd.DataFrame, celltypes: List[str]):
    mat = df[celltypes].astype(float).values
    im = ax.imshow(mat, aspect="auto", cmap=HEAT_CMAP)

    ax.set_yticks(np.arange(len(df.index)))
    ax.set_yticklabels([DISPLAY_NAME.get(m, m) for m in df.index])
    ax.set_xticks(np.arange(len(celltypes)))
    ax.set_xticklabels(celltypes, rotation=45, ha="right")
    ax.set_title("Cell-type-level RMSE", pad=8)

    # White grid.
    ax.set_xticks(np.arange(-0.5, len(celltypes), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(df.index), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=0.4)
    ax.tick_params(which="minor", bottom=False, left=False)

    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("RMSE")
    add_panel_label(ax, "D")


def heatmap_weights(ax, weights: pd.DataFrame):
    weights = weights.copy()
    weights.index = [RENAME_MAP.get(str(x), str(x)) for x in weights.index]

    # Ensure method order and natural cell type order.
    method_order = [m for m in METHOD_ORDER if m in weights.index and m != "CTW-RF"]
    other_methods = [m for m in weights.index if m not in method_order]
    weights = weights.loc[method_order + other_methods]

    celltypes = infer_celltype_columns(weights.T)
    if not celltypes:
        celltypes = list(weights.columns)

    # Natural sort columns.
    def ct_key(x):
        m = re.match(r"^L(\d+)$", str(x))
        return int(m.group(1)) if m else 9999
    cols = sorted(weights.columns, key=ct_key)
    weights = weights[cols]

    im = ax.imshow(weights.values.astype(float), aspect="auto", cmap=WEIGHT_CMAP, vmin=0, vmax=max(1.0, np.nanmax(weights.values)))

    ax.set_yticks(np.arange(len(weights.index)))
    ax.set_yticklabels([DISPLAY_NAME.get(m, m) for m in weights.index])
    ax.set_xticks(np.arange(len(weights.columns)))
    ax.set_xticklabels(weights.columns, rotation=45, ha="right")
    ax.set_title("Average cell-type-wise fusion weights", pad=8)

    ax.set_xticks(np.arange(-0.5, len(weights.columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(weights.index), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=0.4)
    ax.tick_params(which="minor", bottom=False, left=False)

    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Weight")
    add_panel_label(ax, "E")

    return weights


def method_contribution_bar(ax, weights: pd.DataFrame):
    # Sum weights across cell types.
    contrib = weights.sum(axis=1).sort_values(ascending=False)
    colors = [METHOD_COLORS.get(m, BASELINE_COLOR) for m in contrib.index]
    x = np.arange(len(contrib))

    ax.bar(x, contrib.values, color=colors, edgecolor="white", linewidth=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([DISPLAY_NAME.get(m, m) for m in contrib.index], rotation=35, ha="right")
    ax.set_ylabel("Sum of weights\nacross cell types")
    ax.set_title("Overall contribution of candidate methods", pad=8)
    ax.grid(axis="y", alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)

    ylim = ax.get_ylim()
    offset = (ylim[1] - ylim[0]) * 0.015
    for i, v in enumerate(contrib.values):
        ax.text(i, v + offset, f"{v:.2f}", ha="center", va="bottom", fontsize=7.5)

    add_panel_label(ax, "F")


def save_table_and_summary(metrics: pd.DataFrame, celltypes: List[str], weights: pd.DataFrame):
    table = metrics.copy()

    # Winner counts by cell-type RMSE.
    winners = table[celltypes].idxmin(axis=0)
    winner_count = winners.value_counts().to_dict()
    table["best_celltype_count"] = [winner_count.get(m, 0) for m in table.index]

    table["JSD_rank"] = table["JSD"].rank(method="min", ascending=True).astype(int)
    table["aggregated_RMSE_rank"] = table["aggregated_celltype_RMSE"].rank(method="min", ascending=True).astype(int)
    table["mean_rank"] = table[["JSD_rank", "aggregated_RMSE_rank"]].mean(axis=1)

    out_cols = [
        "JSD",
        "matrix_RMSE",
        "aggregated_celltype_RMSE",
        "mean_celltype_RMSE",
        "best_celltype_count",
        "JSD_rank",
        "aggregated_RMSE_rank",
        "mean_rank",
    ]

    table1 = table[out_cols].sort_values(["mean_rank", "aggregated_celltype_RMSE"])
    table1.to_csv(os.path.join(OUT_DIR, "Table1_CTW_RF_metrics.csv"), encoding="utf-8-sig")

    best_rmse_method = table["aggregated_celltype_RMSE"].idxmin()
    best_jsd_method = table["JSD"].idxmin()

    baseline_methods = [m for m in table.index if m != "CTW-RF"]
    best_baseline_rmse = table.loc[baseline_methods, "aggregated_celltype_RMSE"].idxmin()
    best_baseline_jsd = table.loc[baseline_methods, "JSD"].idxmin()

    ctwrf_rmse = float(table.loc["CTW-RF", "aggregated_celltype_RMSE"])
    ctwrf_jsd = float(table.loc["CTW-RF", "JSD"])
    base_rmse = float(table.loc[best_baseline_rmse, "aggregated_celltype_RMSE"])
    base_jsd = float(table.loc[best_baseline_jsd, "JSD"])

    rmse_improve = (base_rmse - ctwrf_rmse) / base_rmse * 100.0
    jsd_improve = (base_jsd - ctwrf_jsd) / base_jsd * 100.0

    summary = []
    summary.append("CTW-RF 5-fold CV paper-style result summary")
    summary.append("=" * 58)
    summary.append("")
    summary.append(f"Best method by aggregated cell-type RMSE: {best_rmse_method}")
    summary.append(f"Best method by JSD: {best_jsd_method}")
    summary.append("")
    summary.append(f"CTW-RF JSD: {ctwrf_jsd:.6f}")
    summary.append(f"CTW-RF aggregated cell-type RMSE: {ctwrf_rmse:.6f}")
    summary.append("")
    summary.append(f"Best baseline by JSD: {best_baseline_jsd}, JSD={base_jsd:.6f}")
    summary.append(f"Best baseline by aggregated cell-type RMSE: {best_baseline_rmse}, RMSE={base_rmse:.6f}")
    summary.append("")
    summary.append(f"CTW-RF improvement vs best baseline by JSD: {jsd_improve:.2f}%")
    summary.append(f"CTW-RF improvement vs best baseline by aggregated cell-type RMSE: {rmse_improve:.2f}%")
    summary.append("")
    summary.append("Cell-type winner counts:")
    for m, n in sorted(winner_count.items(), key=lambda x: (-x[1], x[0])):
        summary.append(f"  {m}: {n}/{len(celltypes)}")
    summary.append("")
    summary.append("Method contribution based on CTW-RF fusion weights:")
    contrib = weights.sum(axis=1).sort_values(ascending=False)
    for m, v in contrib.items():
        summary.append(f"  {m}: {v:.4f}")

    with open(os.path.join(OUT_DIR, "CTW_RF_result_summary.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary))

    return table1


# ============================================================
# 4. Main
# ============================================================
def main():
    set_paper_style()

    metrics = read_csv_smart(METRICS_CSV, index_col=0)
    metrics = normalize_method_index(metrics)

    # Remove duplicate index if both Proposed_CV and CTW-RF exist after renaming.
    metrics = metrics[~metrics.index.duplicated(keep="first")]
    metrics = order_methods(metrics)

    required = ["JSD", "matrix_RMSE", "aggregated_celltype_RMSE", "mean_celltype_RMSE"]
    for col in required:
        if col not in metrics.columns:
            raise ValueError(f"Missing column in metrics: {col}")

    celltypes = infer_celltype_columns(metrics)
    if not celltypes:
        raise ValueError("No cell-type columns inferred from metrics CSV.")

    weights = read_csv_smart(WEIGHTS_CSV, index_col=0)
    weights.index = [RENAME_MAP.get(str(x), str(x)) for x in weights.index]
    weights = weights[~weights.index.duplicated(keep="first")]

    # Save clean paper table and summary.
    table1 = save_table_and_summary(metrics, celltypes, weights)
    print("\n[Table 1]")
    print(table1)

    # Multi-panel figure.
    fig = plt.figure(figsize=(16.5, 10.5))
    gs = gridspec.GridSpec(
        3, 6,
        figure=fig,
        height_ratios=[1.0, 1.0, 1.25],
        hspace=0.55,
        wspace=0.55,
    )

    ax_a = fig.add_subplot(gs[0, 0:2])
    ax_b = fig.add_subplot(gs[0, 2:4])
    ax_c = fig.add_subplot(gs[0, 4:6])
    ax_d = fig.add_subplot(gs[1, 0:6])
    ax_e = fig.add_subplot(gs[2, 0:4])
    ax_f = fig.add_subplot(gs[2, 4:6])

    barplot_metric(
        ax_a,
        metrics,
        "JSD",
        "JSD\n(lower is better)",
        "Distributional similarity",
        "A",
    )

    barplot_metric(
        ax_b,
        metrics,
        "aggregated_celltype_RMSE",
        "Aggregated cell-type RMSE\n(lower is better)",
        "Cell-type-level accuracy",
        "B",
    )

    scatter_tradeoff(ax_c, metrics)
    heatmap_celltype_rmse(ax_d, metrics, celltypes)
    clean_weights = heatmap_weights(ax_e, weights)
    method_contribution_bar(ax_f, clean_weights)

    fig.suptitle("Benchmark performance of CTW-RF under 5-fold cross-validation", y=0.995, fontsize=13)
    fig.savefig(os.path.join(OUT_DIR, "Figure2_CTW_RF_benchmark.png"), dpi=600)
    fig.savefig(os.path.join(OUT_DIR, "Figure2_CTW_RF_benchmark.pdf"))
    fig.savefig(os.path.join(OUT_DIR, "Figure2_CTW_RF_benchmark.svg"))
    plt.close(fig)

    # Also save a simple standalone table as Excel-friendly CSV.
    print("\nSaved outputs to:")
    print(OUT_DIR)
    print("\nMain figure:")
    print(os.path.join(OUT_DIR, "Figure2_CTW_RF_benchmark.png"))
    print(os.path.join(OUT_DIR, "Figure2_CTW_RF_benchmark.pdf"))
    print("\nTable:")
    print(os.path.join(OUT_DIR, "Table1_CTW_RF_metrics.csv"))
    print("\nSummary:")
    print(os.path.join(OUT_DIR, "CTW_RF_result_summary.txt"))


if __name__ == "__main__":
    main()
