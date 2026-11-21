import os
import json
import numpy as np
import pandas as pd

# ============================================================
# 1. 路径设置
# ============================================================
SRC_DIR = r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz"

OUT_DIR = r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots"
os.makedirs(OUT_DIR, exist_ok=True)

SC_COUNTS_PATH = os.path.join(SRC_DIR, "sc_reference_counts.csv")
SC_LABELS_PATH = os.path.join(SRC_DIR, "sc_reference_labels.csv")

# ============================================================
# 2. 扩容参数
# ============================================================
SEED = 2026

N_SPOTS = 2000       # 先扩到 2000
N_MIX_CELLS = 8      # 每个 pseudo-spot 混合 8 个 single cells

# balanced_celltype:
#   每次先均匀抽 cell type，再从该 cell type 中抽细胞。
#   好处：19 个 cell type 都会比较充分出现，适合 benchmark。
#
# cell_uniform:
#   直接从所有细胞中随机抽。
#   好处：更接近原始细胞丰度；坏处：稀有类型可能几乎不出现。
SAMPLING_MODE = "balanced_celltype"

# 表达矩阵生成方式：
# sum_counts: 直接把 8 个细胞 counts 相加，保持整数 counts，更接近真实 spot count
# mean_counts: 求平均，数值更平滑
EXPR_MODE = "sum_counts"

rng = np.random.default_rng(SEED)

# ============================================================
# 3. 工具函数
# ============================================================
def detect_label_column(labels_df):
    candidates = [
        "label",
        "cell_type",
        "CellType",
        "celltype",
        "annotation",
        "type",
        "cluster",
    ]

    for c in candidates:
        if c in labels_df.columns:
            return c

    raise ValueError(
        "找不到细胞类型标签列。当前 sc_reference_labels.csv 的列为：\n"
        + str(list(labels_df.columns))
    )


def detect_xy_columns(labels_df):
    x_candidates = ["X", "x", "centroid_x", "cell_x", "global_x"]
    y_candidates = ["Y", "y", "centroid_y", "cell_y", "global_y"]

    x_col = None
    y_col = None

    for c in x_candidates:
        if c in labels_df.columns:
            x_col = c
            break

    for c in y_candidates:
        if c in labels_df.columns:
            y_col = c
            break

    return x_col, y_col


def safe_cell_uid_column(df):
    candidates = ["cell_uid", "cell_id", "CellID", "cell"]
    for c in candidates:
        if c in df.columns:
            return c
    return df.columns[0]


def normalize_rows(df):
    arr = df.values.astype(float)
    arr[arr < 0] = 0

    rs = arr.sum(axis=1, keepdims=True)
    rs[rs == 0] = 1.0

    arr = arr / rs
    return pd.DataFrame(arr, index=df.index, columns=df.columns)


# ============================================================
# 4. 读取 single-cell reference
# ============================================================
print("Reading sc_reference_counts.csv ...")
sc_counts = pd.read_csv(SC_COUNTS_PATH)

print("Reading sc_reference_labels.csv ...")
sc_labels = pd.read_csv(SC_LABELS_PATH)

print("raw sc_counts shape:", sc_counts.shape)
print("raw sc_labels shape:", sc_labels.shape)

# -------------------------
# 设置 cell_uid 为 index
# -------------------------
counts_uid_col = safe_cell_uid_column(sc_counts)
labels_uid_col = safe_cell_uid_column(sc_labels)

print("counts_uid_col:", counts_uid_col)
print("labels_uid_col:", labels_uid_col)

sc_counts[counts_uid_col] = sc_counts[counts_uid_col].astype(str)
sc_labels[labels_uid_col] = sc_labels[labels_uid_col].astype(str)

sc_counts = sc_counts.set_index(counts_uid_col)
sc_labels = sc_labels.set_index(labels_uid_col)

# 如果 labels 里面有重复 cell_uid，保留第一条
sc_labels = sc_labels[~sc_labels.index.duplicated(keep="first")]

# -------------------------
# 对齐 cells
# -------------------------
common_cells = sc_counts.index.intersection(sc_labels.index)

if len(common_cells) == 0:
    raise ValueError("sc_reference_counts 和 sc_reference_labels 没有共同 cell_uid。")

sc_counts = sc_counts.loc[common_cells].copy()
sc_labels = sc_labels.loc[common_cells].copy()

print("common cells:", len(common_cells))

# -------------------------
# 检测 label / coordinate
# -------------------------
label_col = detect_label_column(sc_labels)
x_col, y_col = detect_xy_columns(sc_labels)

print("label_col:", label_col)
print("x_col:", x_col)
print("y_col:", y_col)

labels = sc_labels[label_col].astype(str)

cell_types = sorted(labels.unique().tolist())
print("n cell types:", len(cell_types))
print(cell_types)

# -------------------------
# counts 转成数值矩阵
# -------------------------
sc_counts = sc_counts.apply(pd.to_numeric, errors="coerce").fillna(0)
sc_counts[sc_counts < 0] = 0

genes = sc_counts.columns.tolist()
cell_ids = sc_counts.index.to_numpy()
label_arr = labels.loc[cell_ids].to_numpy()

X = sc_counts.values.astype(np.float32)

print("X shape:", X.shape)

# 每个 cell type 对应的细胞 index
ct_to_indices = {}
for ct in cell_types:
    idx = np.where(label_arr == ct)[0]
    ct_to_indices[ct] = idx
    print(ct, "n_cells =", len(idx))

# 坐标
has_xy = x_col is not None and y_col is not None

if has_xy:
    cell_x = pd.to_numeric(sc_labels.loc[cell_ids, x_col], errors="coerce").to_numpy()
    cell_y = pd.to_numeric(sc_labels.loc[cell_ids, y_col], errors="coerce").to_numpy()

    # 坐标缺失时用 0 填充
    cell_x = np.nan_to_num(cell_x, nan=0.0)
    cell_y = np.nan_to_num(cell_y, nan=0.0)

    print("Using real cell coordinates from labels.")
else:
    print("[WARN] No X/Y columns found. Synthetic coordinates will be generated.")
    cell_x = None
    cell_y = None

# ============================================================
# 5. 生成 pseudo-spots
# ============================================================
pseudo_expr_list = []
pseudo_gt_list = []
pseudo_gt_count_list = []
pseudo_loc_list = []

n_cells_total = X.shape[0]

print("\nGenerating pseudo-spots ...")

for s in range(N_SPOTS):
    spot_id = f"SYN{s:05d}"

    # -------------------------
    # 选择要混合的 cells
    # -------------------------
    if SAMPLING_MODE == "balanced_celltype":
        selected_cell_indices = []

        for _ in range(N_MIX_CELLS):
            ct = rng.choice(cell_types)
            candidate_indices = ct_to_indices[ct]

            # 极端情况下某个 cell type 没细胞，跳过
            if len(candidate_indices) == 0:
                selected_cell_indices.append(rng.integers(0, n_cells_total))
            else:
                selected_cell_indices.append(rng.choice(candidate_indices))

        selected_cell_indices = np.array(selected_cell_indices, dtype=int)

    elif SAMPLING_MODE == "cell_uniform":
        selected_cell_indices = rng.choice(
            np.arange(n_cells_total),
            size=N_MIX_CELLS,
            replace=True
        )

    else:
        raise ValueError("Unknown SAMPLING_MODE: " + str(SAMPLING_MODE))

    selected_labels = label_arr[selected_cell_indices]

    # -------------------------
    # 生成 expression
    # -------------------------
    selected_expr = X[selected_cell_indices, :]

    if EXPR_MODE == "sum_counts":
        spot_expr = selected_expr.sum(axis=0)
    elif EXPR_MODE == "mean_counts":
        spot_expr = selected_expr.mean(axis=0)
    else:
        raise ValueError("Unknown EXPR_MODE: " + str(EXPR_MODE))

    pseudo_expr_list.append(spot_expr)

    # -------------------------
    # 生成 ground truth
    # -------------------------
    gt_counts = {ct: 0 for ct in cell_types}

    for lab in selected_labels:
        gt_counts[lab] += 1

    gt_props = {ct: gt_counts[ct] / float(N_MIX_CELLS) for ct in cell_types}

    pseudo_gt_count_list.append([gt_counts[ct] for ct in cell_types])
    pseudo_gt_list.append([gt_props[ct] for ct in cell_types])

    # -------------------------
    # 生成 pseudo location
    # -------------------------
    if has_xy:
        x = float(np.mean(cell_x[selected_cell_indices]))
        y = float(np.mean(cell_y[selected_cell_indices]))

        # 加一点极小 jitter，避免多个点完全重叠
        x = x + float(rng.normal(0, 1e-3))
        y = y + float(rng.normal(0, 1e-3))

        fov = -1
    else:
        # 没有真实坐标时，放到规则网格上
        grid_w = int(np.ceil(np.sqrt(N_SPOTS)))
        x = float(s % grid_w)
        y = float(s // grid_w)
        fov = -1

    pseudo_loc_list.append({
        "spot_id": spot_id,
        "fov": fov,
        "x": x,
        "y": y,
        "n_cells": N_MIX_CELLS
    })

    if (s + 1) % 200 == 0:
        print(f"generated {s + 1}/{N_SPOTS}")

# ============================================================
# 6. 保存结果
# ============================================================
print("\nSaving outputs ...")

pseudo_expr = pd.DataFrame(
    pseudo_expr_list,
    index=[f"SYN{s:05d}" for s in range(N_SPOTS)],
    columns=genes
)
pseudo_expr.index.name = "spot_id"

pseudo_gt = pd.DataFrame(
    pseudo_gt_list,
    index=pseudo_expr.index,
    columns=cell_types
)
pseudo_gt.index.name = "spot_id"

pseudo_gt_counts = pd.DataFrame(
    pseudo_gt_count_list,
    index=pseudo_expr.index,
    columns=cell_types
)
pseudo_gt_counts.index.name = "spot_id"

pseudo_locs = pd.DataFrame(pseudo_loc_list)
pseudo_locs = pseudo_locs.set_index("spot_id")
pseudo_locs.index.name = "spot_id"

# 行归一化检查
pseudo_gt = normalize_rows(pseudo_gt)

# 保存 pseudo benchmark
pseudo_expr.to_csv(os.path.join(OUT_DIR, "pseudo_spot_expression.csv"))
pseudo_gt.to_csv(os.path.join(OUT_DIR, "pseudo_spot_ground_truth.csv"))
pseudo_gt_counts.to_csv(os.path.join(OUT_DIR, "pseudo_spot_ground_truth_counts.csv"))
pseudo_locs.to_csv(os.path.join(OUT_DIR, "pseudo_spot_locations.csv"))

# 保存 reference，保持目录自洽
sc_counts_out = sc_counts.copy()
sc_counts_out.index.name = "cell_uid"
sc_counts_out.to_csv(os.path.join(OUT_DIR, "sc_reference_counts.csv"))

sc_labels_out = sc_labels.copy()
sc_labels_out.index.name = "cell_uid"
sc_labels_out.to_csv(os.path.join(OUT_DIR, "sc_reference_labels.csv"))

# 保存 cell metadata，方便之后查看
cell_metadata = sc_labels.copy()
cell_metadata.index.name = "cell_uid"
cell_metadata.to_csv(os.path.join(OUT_DIR, "cell_metadata_merged.csv"))

# 保存配置
config = {
    "source_dir": SRC_DIR,
    "out_dir": OUT_DIR,
    "seed": SEED,
    "n_spots": N_SPOTS,
    "n_mix_cells": N_MIX_CELLS,
    "sampling_mode": SAMPLING_MODE,
    "expr_mode": EXPR_MODE,
    "n_cells_reference": int(n_cells_total),
    "n_genes": int(len(genes)),
    "n_cell_types": int(len(cell_types)),
    "cell_types": cell_types,
    "label_col": label_col,
    "x_col": x_col,
    "y_col": y_col,
}

with open(os.path.join(OUT_DIR, "build_config.json"), "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

# ============================================================
# 7. 输出检查
# ============================================================
print("\nDONE")
print("Saved to:", OUT_DIR)
print("pseudo_expr:", pseudo_expr.shape)
print("pseudo_gt:", pseudo_gt.shape)
print("pseudo_gt_counts:", pseudo_gt_counts.shape)
print("pseudo_locs:", pseudo_locs.shape)
print("sc_counts:", sc_counts.shape)
print("sc_labels:", sc_labels.shape)

print("\nGround truth row sum range:")
print(pseudo_gt.sum(axis=1).min(), pseudo_gt.sum(axis=1).max())

print("\nFirst 5 pseudo spots:")
print(pseudo_gt.head())

print("\nCell type total proportions across all synthetic spots:")
print(pseudo_gt.mean(axis=0).sort_values(ascending=False))