import os
import numpy as np
import pandas as pd

# =========================================================
# 0. 路径配置
# =========================================================
BASE_DIR = r"D:\Research\STdeconv_benchmark\data\groundtruth"

CENTROIDS_PATH = os.path.join(BASE_DIR, "cortex_svz_cellcentroids.csv")
ANNOT_PATH     = os.path.join(BASE_DIR, "cortex_svz_cell_type_annotations.csv")
COUNTS_PATH    = os.path.join(BASE_DIR, "cortex_svz_counts.csv")

OUT_DIR = os.path.join(BASE_DIR, "self_benchmark_cortex_svz")
os.makedirs(OUT_DIR, exist_ok=True)

# =========================================================
# 1. 可调参数
# =========================================================
BIN_SIZE = 250
MIN_CELLS_PER_SPOT = 2
REGION_FILTER = None   # 例如 ["Cortex"] / ["SVZ"] / None

# =========================================================
# 2. 读取数据
# =========================================================
centroids = pd.read_csv(CENTROIDS_PATH)
annot = pd.read_csv(ANNOT_PATH)
counts = pd.read_csv(COUNTS_PATH)

print("centroids shape:", centroids.shape)
print("annot shape:", annot.shape)
print("counts shape:", counts.shape)

# =========================================================
# 3. 基础检查与对齐
# =========================================================
n_cells = counts.shape[0]

if centroids.shape[0] != n_cells or annot.shape[0] != n_cells:
    raise ValueError(
        f"三份文件细胞数不一致: centroids={centroids.shape[0]}, annot={annot.shape[0]}, counts={n_cells}"
    )

annot = annot.copy()
annot["cell_id"] = annot["index"] + 1

counts = counts.copy()
counts["cell_id"] = np.arange(1, n_cells + 1)

meta = centroids.merge(
    annot[["cell_id", "louvain"]],
    left_on="Cell ID",
    right_on="cell_id",
    how="inner"
)

if meta.shape[0] != n_cells:
    raise ValueError(f"metadata 合并后细胞数不对: {meta.shape[0]} != {n_cells}")

counts = counts.merge(
    meta[["cell_id"]],
    on="cell_id",
    how="inner"
)

meta = meta.sort_values("cell_id").reset_index(drop=True)
counts = counts.sort_values("cell_id").reset_index(drop=True)

assert np.all(meta["cell_id"].to_numpy() == counts["cell_id"].to_numpy())

# =========================================================
# 4. 可选区域过滤
# =========================================================
if REGION_FILTER is not None:
    mask = meta["Region"].isin(REGION_FILTER)
    meta = meta.loc[mask].reset_index(drop=True)
    counts = counts.loc[mask].reset_index(drop=True)

print("after region filter:")
print("meta shape:", meta.shape)
print("counts shape:", counts.shape)
print("Region counts:")
print(meta["Region"].value_counts())

# =========================================================
# 5. 构造 pseudo-spot
# =========================================================
meta["bin_x"] = np.floor(meta["X"] / BIN_SIZE).astype(int)
meta["bin_y"] = np.floor(meta["Y"] / BIN_SIZE).astype(int)

meta["spot_id"] = (
    "FOV" + meta["Field of View"].astype(str)
    + "_X" + meta["bin_x"].astype(str)
    + "_Y" + meta["bin_y"].astype(str)
)

spot_sizes = meta["spot_id"].value_counts().rename("n_cells")
valid_spots = spot_sizes[spot_sizes >= MIN_CELLS_PER_SPOT].index

meta = meta[meta["spot_id"].isin(valid_spots)].reset_index(drop=True)
counts = counts.loc[meta.index].copy()

print("after spot filter:")
print("n valid spots:", meta["spot_id"].nunique())
print("n valid cells:", meta.shape[0])

# =========================================================
# 6. 构造 spot × gene 表达矩阵
# =========================================================
gene_cols = [c for c in counts.columns if c != "cell_id"]

counts_with_spot = counts[gene_cols].copy()
counts_with_spot["spot_id"] = meta["spot_id"].values

spot_expr = counts_with_spot.groupby("spot_id", sort=False).sum()

print("spot_expr shape:", spot_expr.shape)

# =========================================================
# 7. 构造 spot 坐标
# =========================================================
spot_loc = meta.groupby("spot_id", sort=False).agg(
    fov=("Field of View", "first"),
    x=("X", "mean"),
    y=("Y", "mean"),
    n_cells=("spot_id", "size")
)

print("spot_loc shape:", spot_loc.shape)

# =========================================================
# 8. 构造 ground truth: spot × louvain proportion
# =========================================================
meta["louvain_str"] = "L" + meta["louvain"].astype(str)

spot_gt_count = pd.crosstab(meta["spot_id"], meta["louvain_str"])
spot_gt_prop = spot_gt_count.div(spot_gt_count.sum(axis=1), axis=0)

print("spot_gt_prop shape:", spot_gt_prop.shape)

# =========================================================
# 9. 导出单细胞参考（改成全局唯一 cell_uid）
# =========================================================
meta["cell_uid"] = (
    "FOV" + meta["Field of View"].astype(str) +
    "_C" + meta["cell_id"].astype(str)
)

sc_counts = counts[gene_cols].copy()
sc_counts.index = meta["cell_uid"].astype(str)

sc_labels = meta[["cell_uid", "cell_id", "louvain_str", "Region", "Field of View", "X", "Y"]].copy()
sc_labels = sc_labels.rename(columns={"louvain_str": "label"})
sc_labels.index = sc_labels["cell_uid"].astype(str)
# =========================================================
# 10. 保存文件
# =========================================================
spot_expr_path = os.path.join(OUT_DIR, "pseudo_spot_expression.csv")
spot_loc_path = os.path.join(OUT_DIR, "pseudo_spot_locations.csv")
spot_gt_path = os.path.join(OUT_DIR, "pseudo_spot_ground_truth.csv")
spot_count_path = os.path.join(OUT_DIR, "pseudo_spot_ground_truth_counts.csv")
sc_counts_path = os.path.join(OUT_DIR, "sc_reference_counts.csv")
sc_labels_path = os.path.join(OUT_DIR, "sc_reference_labels.csv")
meta_path = os.path.join(OUT_DIR, "cell_metadata_merged.csv")

spot_expr.to_csv(spot_expr_path)
spot_loc.to_csv(spot_loc_path)
spot_gt_prop.to_csv(spot_gt_path)
spot_gt_count.to_csv(spot_count_path)
sc_counts.to_csv(sc_counts_path)
sc_labels.to_csv(sc_labels_path)
meta.to_csv(meta_path, index=False)

print("\nDONE")
print("Saved files:")
print(spot_expr_path)
print(spot_loc_path)
print(spot_gt_path)
print(spot_count_path)
print(sc_counts_path)
print(sc_labels_path)
print(meta_path)

# =========================================================
# 11. 简单摘要
# =========================================================
summary = {
    "BIN_SIZE": BIN_SIZE,
    "MIN_CELLS_PER_SPOT": MIN_CELLS_PER_SPOT,
    "REGION_FILTER": REGION_FILTER,
    "n_cells_used": int(meta.shape[0]),
    "n_spots": int(spot_expr.shape[0]),
    "n_genes": int(spot_expr.shape[1]),
    "n_clusters": int(spot_gt_prop.shape[1]),
    "min_cells_in_spot": int(spot_loc["n_cells"].min()),
    "max_cells_in_spot": int(spot_loc["n_cells"].max()),
    "mean_cells_in_spot": float(spot_loc["n_cells"].mean()),
}
print("\nSummary:")
for k, v in summary.items():
    print(f"{k}: {v}")