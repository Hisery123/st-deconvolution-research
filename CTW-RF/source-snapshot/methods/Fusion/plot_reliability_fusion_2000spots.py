# -*- coding: utf-8 -*-
"""
Plot reliability-aware ensemble fusion results for self_benchmark_cortex_svz_2000spots.

先运行：run_reliability_fusion_2000spots.py
再运行：python "D:/Research/STdeconv_benchmark/evaluation & visualization/plot_reliability_fusion_2000spots.py"
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 1. 路径配置
# ============================================================
BASE_DIR = r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots"
PRED_DIR = os.path.join(BASE_DIR, "predictions")
EVAL_DIR = r"D:\Research\STdeconv_benchmark\evaluation & visualization\reliability_fusion_2000spots"
FIG_DIR = os.path.join(EVAL_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

OUT_PREFIX = "self2000_reliability_fusion"
METRICS_CSV = os.path.join(EVAL_DIR, f"{OUT_PREFIX}_metrics_summary.csv")
IMPROVE_CSV = os.path.join(EVAL_DIR, f"{OUT_PREFIX}_improvement_vs_best_baseline.csv")
BEST_WEIGHTS_CSV = os.path.join(EVAL_DIR, "Proposed_best_weights.csv")

# 只用于主图展示。存在就展示，不存在就跳过。
BASELINE_ORDER = [
    "Tangram",
    "RCTD",
    "CellDART",
    "CARD",
    "cell2location",
    "SPOTlight",
]

# 主图里 Proposed 只放最强版本，其他 proposed 做扩展图
BEST_PROPOSED_NAME = "Proposed_best"

DISPLAY_NAME = {
    "Tangram": "Tangram",
    "RCTD": "RCTD",
    "CellDART": "CellDART",
    "CARD": "CARD",
    "cell2location": "cell2location",
    "SPOTlight": "SPOTlight",
    "Proposed_best": "Proposed",
}

# ============================================================
# 2. 工具函数
# ============================================================
def savefig(name: str):
    png = os.path.join(FIG_DIR, name + ".png")
    pdf = os.path.join(FIG_DIR, name + ".pdf")
    plt.tight_layout()
    plt.savefig(png, dpi=300)
    plt.savefig(pdf)
    plt.close()
    print("saved:", png)
    print("saved:", pdf)


def as_numeric(df: pd.DataFrame, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def label_list(index):
    return [DISPLAY_NAME.get(x, x) for x in index]


def get_celltype_cols(metrics: pd.DataFrame):
    meta = {
        "display_name", "method_group", "JSD", "total_RMSE", "mean_RMSE",
        "JSD_rank", "total_RMSE_rank", "mean_rank"
    }
    cols = [c for c in metrics.columns if c not in meta]
    # 保留形如 L数字 的列
    cols = [c for c in cols if re.fullmatch(r"L\d+", str(c))]
    return cols


def build_main_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    """主图：baseline + best proposed。"""
    baseline = [m for m in BASELINE_ORDER if m in metrics.index]

    proposed_metrics = metrics[metrics["method_group"] == "proposed"].copy()
    proposed_metrics["total_RMSE"] = pd.to_numeric(proposed_metrics["total_RMSE"])
    proposed_metrics["JSD"] = pd.to_numeric(proposed_metrics["JSD"])
    best_prop_id = proposed_metrics.sort_values(["total_RMSE", "JSD"]).index[0]

    main = metrics.loc[baseline + [best_prop_id]].copy()
    main = main.rename(index={best_prop_id: BEST_PROPOSED_NAME})
    main.loc[BEST_PROPOSED_NAME, "display_name"] = "Proposed"
    return main


def barplot_metric(df: pd.DataFrame, metric: str, ylabel: str, title: str, filename: str):
    vals = pd.to_numeric(df[metric], errors="coerce")
    x = np.arange(len(df.index))

    plt.figure(figsize=(9.2, 4.8))
    plt.bar(x, vals.values)
    plt.xticks(x, label_list(df.index), rotation=25, ha="right")
    plt.ylabel(ylabel)
    plt.title(title)

    for i, v in enumerate(vals.values):
        if pd.notna(v):
            plt.text(i, v, f"{v:.4f}", ha="center", va="bottom", fontsize=8)

    savefig(filename)


def improvement_barplot(improve: pd.DataFrame, col: str, ylabel: str, title: str, filename: str):
    main_idx = [m for m in BASELINE_ORDER if m in improve.index]

    proposed = improve[improve["method_group"] == "proposed"].copy()
    proposed[col] = pd.to_numeric(proposed[col], errors="coerce")
    # 只拿 best proposed
    best_prop = proposed.sort_values(col, ascending=False).index[0]

    use = improve.loc[main_idx + [best_prop]].copy()
    use = use.rename(index={best_prop: BEST_PROPOSED_NAME})
    vals = pd.to_numeric(use[col], errors="coerce")
    x = np.arange(len(use.index))

    plt.figure(figsize=(9.2, 4.8))
    plt.bar(x, vals.values)
    plt.axhline(0, linewidth=1)
    plt.xticks(x, label_list(use.index), rotation=25, ha="right")
    plt.ylabel(ylabel)
    plt.title(title)

    for i, v in enumerate(vals.values):
        if pd.notna(v):
            va = "bottom" if v >= 0 else "top"
            plt.text(i, v, f"{v:.2f}%", ha="center", va=va, fontsize=8)

    savefig(filename)


# ============================================================
# 3. 读取结果
# ============================================================
if not os.path.exists(METRICS_CSV):
    raise FileNotFoundError("Metrics CSV not found. Run run_reliability_fusion_2000spots.py first: " + METRICS_CSV)

metrics = pd.read_csv(METRICS_CSV, index_col=0)
metrics = as_numeric(metrics, ["JSD", "total_RMSE", "mean_RMSE", "JSD_rank", "total_RMSE_rank", "mean_rank"])

print("[Metrics]")
print(metrics[["display_name", "method_group", "JSD", "total_RMSE", "JSD_rank", "total_RMSE_rank", "mean_rank"]])

main = build_main_metrics(metrics)
celltype_cols = get_celltype_cols(metrics)

# ============================================================
# 4. 主图：总体指标
# ============================================================
barplot_metric(
    main,
    "JSD",
    "JSD (lower is better)",
    "Reliability fusion benchmark: JSD",
    "01_main_JSD_barplot",
)

barplot_metric(
    main,
    "total_RMSE",
    "total_RMSE / Sum of cell-type RMSE (lower is better)",
    "Reliability fusion benchmark: total_RMSE",
    "02_main_total_RMSE_barplot",
)

# scatter: JSD vs total_RMSE
plt.figure(figsize=(6.8, 5.6))
for idx in main.index:
    x = float(main.loc[idx, "JSD"])
    y = float(main.loc[idx, "total_RMSE"])
    plt.scatter(x, y, s=80)
    plt.text(x, y, " " + DISPLAY_NAME.get(idx, idx), fontsize=9, va="center")
plt.xlabel("JSD (lower is better)")
plt.ylabel("total_RMSE (lower is better)")
plt.title("Overall performance trade-off")
savefig("03_main_JSD_RMSE_scatter")

# ============================================================
# 5. improvement vs best baseline
# ============================================================
if os.path.exists(IMPROVE_CSV):
    improve = pd.read_csv(IMPROVE_CSV, index_col=0)
    improve = as_numeric(improve, [
        "JSD_improvement_percent_vs_best_baseline",
        "RMSE_improvement_percent_vs_best_baseline",
    ])

    improvement_barplot(
        improve,
        "JSD_improvement_percent_vs_best_baseline",
        "JSD improvement vs best baseline (%)",
        "JSD improvement relative to best baseline",
        "04_JSD_improvement_vs_best_baseline",
    )

    improvement_barplot(
        improve,
        "RMSE_improvement_percent_vs_best_baseline",
        "RMSE improvement vs best baseline (%)",
        "total_RMSE improvement relative to best baseline",
        "05_RMSE_improvement_vs_best_baseline",
    )
else:
    print("[WARN] improvement csv not found:", IMPROVE_CSV)

# ============================================================
# 6. cell-type RMSE 分组柱状图和 heatmap
# ============================================================
if len(celltype_cols) > 0:
    ct_df = main[celltype_cols].apply(pd.to_numeric, errors="coerce")

    # grouped barplot
    clusters = celltype_cols
    methods = list(ct_df.index)
    x = np.arange(len(clusters))
    width = 0.82 / max(len(methods), 1)

    plt.figure(figsize=(max(14, len(clusters) * 0.65), 6.4))
    for i, method in enumerate(methods):
        plt.bar(
            x + i * width - (len(methods) - 1) * width / 2,
            ct_df.loc[method, clusters].values,
            width=width,
            label=DISPLAY_NAME.get(method, method),
        )

    plt.xticks(x, clusters, rotation=45, ha="right")
    plt.ylabel("Cell-type RMSE (lower is better)")
    plt.title("Per-cell-type RMSE comparison")
    plt.legend(ncol=2, fontsize=8)
    savefig("06_celltype_RMSE_grouped_barplot")

    # heatmap
    plt.figure(figsize=(max(12, len(clusters) * 0.48), 5.2))
    im = plt.imshow(ct_df.values, aspect="auto")
    plt.yticks(range(len(methods)), label_list(methods))
    plt.xticks(range(len(clusters)), clusters, rotation=45, ha="right")
    plt.title("Cell-type RMSE heatmap")
    plt.colorbar(im, label="RMSE")
    savefig("07_celltype_RMSE_heatmap")

    # winner count: each cell type which method is best among main
    winners = ct_df.idxmin(axis=0)
    win_counts = winners.value_counts()
    plt.figure(figsize=(7.8, 4.8))
    plt.bar(np.arange(len(win_counts)), win_counts.values)
    plt.xticks(np.arange(len(win_counts)), label_list(win_counts.index), rotation=25, ha="right")
    plt.ylabel("Number of best cell types")
    plt.title("Cell-type winner count")
    for i, v in enumerate(win_counts.values):
        plt.text(i, v, str(v), ha="center", va="bottom", fontsize=9)
    savefig("08_celltype_winner_count")

# ============================================================
# 7. proposed variants 总览
# ============================================================
proposed_all = metrics[metrics["method_group"] == "proposed"].copy()
if len(proposed_all) > 0:
    proposed_all = proposed_all.sort_values(["total_RMSE", "JSD"])

    plt.figure(figsize=(max(10, len(proposed_all) * 0.5), 4.8))
    x = np.arange(len(proposed_all.index))
    vals = proposed_all["total_RMSE"].astype(float).values
    plt.bar(x, vals)
    plt.xticks(x, proposed_all.index, rotation=45, ha="right")
    plt.ylabel("total_RMSE (lower is better)")
    plt.title("Proposed candidate variants")
    savefig("09_proposed_variants_total_RMSE")

# ============================================================
# 8. best weight heatmap
# ============================================================
if os.path.exists(BEST_WEIGHTS_CSV):
    W = pd.read_csv(BEST_WEIGHTS_CSV, index_col=0)
    W = W.apply(pd.to_numeric, errors="coerce").fillna(0.0)

    plt.figure(figsize=(max(7.5, len(W.columns) * 1.0), max(6, len(W.index) * 0.28)))
    im = plt.imshow(W.values, aspect="auto", vmin=0, vmax=max(1e-9, np.nanmax(W.values)))
    plt.yticks(range(len(W.index)), W.index)
    plt.xticks(range(len(W.columns)), W.columns, rotation=35, ha="right")
    plt.title("Proposed best: cell-type-wise reliability weights")
    plt.colorbar(im, label="Weight")
    savefig("10_best_weight_heatmap")

    # 每个方法总权重
    method_weight_sum = W.sum(axis=0).sort_values(ascending=False)
    plt.figure(figsize=(7.8, 4.8))
    plt.bar(np.arange(len(method_weight_sum)), method_weight_sum.values)
    plt.xticks(np.arange(len(method_weight_sum)), method_weight_sum.index, rotation=25, ha="right")
    plt.ylabel("Sum of weights across cell types")
    plt.title("Overall contribution of candidate methods")
    for i, v in enumerate(method_weight_sum.values):
        plt.text(i, v, f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    savefig("11_method_weight_sum")
else:
    print("[WARN] best weights csv not found:", BEST_WEIGHTS_CSV)

print("\nDone.")
print("Figures saved to:", FIG_DIR)
