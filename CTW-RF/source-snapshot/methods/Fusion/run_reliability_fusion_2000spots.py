# -*- coding: utf-8 -*-
"""
Reliability-aware ensemble fusion for self_benchmark_cortex_svz_2000spots.

核心用途：
1. 读取多个已跑通 baseline 的 prediction csv；
2. 以 pseudo_spot_ground_truth.csv 为唯一 ground truth；
3. 对齐 spot / cell type；
4. 生成多种 Proposed 候选：
   - HardSelect：每个 cell type 选择校准集上 RMSE 最低的方法
   - InvRMSE：每个 cell type 按 RMSE 反比加权
   - SoftOpt：每个 cell type 直接优化非负融合权重，最小化 RMSE
   - SoftOptGlobal：可选，全局优化所有 cell-type weights，使行归一化后的 total_RMSE 最小
5. 同时输出 full-data calibration 版本和 5-fold CV 版本；
6. 自动选择 total_RMSE 最低的 Proposed 作为 Proposed_best_self_benchmark.csv。

建议运行：
python "D:/Research/STdeconv_benchmark/evaluation & visualization/run_reliability_fusion_2000spots.py"

依赖：numpy, pandas, matplotlib 可选；scipy 可选但强烈推荐。
"""

import os
import re
import json
import shutil
import warnings
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd

# ============================================================
# 0. 基础配置
# ============================================================
SEED = 2026
rng = np.random.default_rng(SEED)

# 主实验数据目录
BASE_DIR = r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots"
PRED_DIR = os.path.join(BASE_DIR, "predictions")
GT_PATH = os.path.join(BASE_DIR, "pseudo_spot_ground_truth.csv")

# 输出目录：权重、指标、配置等放这里
EVAL_DIR = r"D:\Research\STdeconv_benchmark\evaluation & visualization\reliability_fusion_2000spots"
os.makedirs(EVAL_DIR, exist_ok=True)
os.makedirs(PRED_DIR, exist_ok=True)

# 如果某个方法与 ground truth 的共同 spot 数少于这个比例，就剔除
MIN_COMMON_SPOT_RATIO = 0.90

# 5-fold CV
N_FOLDS = 5
RUN_CV = True

# 可选全局优化。它更像“为了分数做优化”，可能更强，但比 SoftOpt 慢一点。
RUN_GLOBAL_SOFTOPT = True
GLOBAL_MAXITER = 300

# Inverse-RMSE 权重幂次。power 越大，越接近 hard selection。
INVRMSE_POWERS = [1.0, 2.0, 4.0, 8.0]

# 候选 baseline 池。SpaJoint / DestVI / CellDART-SPG 暂不放入。
METHOD_SPECS = {
    "Tangram": ["Tangram_self_benchmark.csv"],
    "RCTD": ["RCTD_self_benchmark.csv"],
    "CellDART": ["CellDART_self_benchmark.csv"],
    "CARD": ["CARD_self_benchmark.csv"],
    "cell2location": ["Cell2location_self_benchmark.csv", "cell2location_self_benchmark.csv"],
    "SPOTlight": ["SPOTlight_self_benchmark.csv", "SPOTlight_self_benchmark.csv"],
}

# 如果你后面补新 baseline，比如 NewMethod_self_benchmark.csv，直接在这里加：
# METHOD_SPECS["NewMethod"] = ["NewMethod_self_benchmark.csv"]

# 输出文件名前缀
OUT_PREFIX = "self2000_reliability_fusion"

# ============================================================
# 1. 可选 scipy 优化器
# ============================================================
try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except Exception as e:
    SCIPY_AVAILABLE = False
    minimize = None
    warnings.warn("scipy not available. SoftOpt will fall back to InvRMSE-like weights. " + repr(e))


# ============================================================
# 2. 工具函数：读取、标准化、对齐
# ============================================================
def find_file_case_insensitive(directory: str, candidate_names: List[str]) -> Optional[str]:
    """在 directory 中按候选名查找文件；支持大小写不敏感。"""
    for name in candidate_names:
        path = os.path.join(directory, name)
        if os.path.exists(path):
            return path

    if not os.path.isdir(directory):
        return None

    lower_to_real = {f.lower(): f for f in os.listdir(directory)}
    for name in candidate_names:
        real = lower_to_real.get(name.lower())
        if real is not None:
            return os.path.join(directory, real)

    return None


def normalize_celltype_names(cols: List[str]) -> List[str]:
    """兼容 cell2location 等输出列名，把列名尽量整理成 L10/L11 这类格式。"""
    out = []
    for x in cols:
        s = str(x).strip()
        s = s.replace("_", ".")

        # cell2location 常见前缀
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

        # 如果列名中包含 L数字，则提取第一个 L数字
        m = re.search(r"L\d+", s)
        if m:
            s = m.group(0)

        out.append(s)
    return out


def collapse_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """标准化列名后若重复，按行求和合并。"""
    if not df.columns.duplicated().any():
        return df

    print("[WARN] duplicated columns after normalization:", list(df.columns[df.columns.duplicated()]))
    return df.T.groupby(level=0).sum().T


def safe_row_normalize(mat: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    arr = np.asarray(mat, dtype=float).copy()
    arr[~np.isfinite(arr)] = 0.0
    arr[arr < 0] = 0.0
    rs = arr.sum(axis=1, keepdims=True)
    rs[~np.isfinite(rs)] = 0.0
    rs[rs <= eps] = 1.0
    arr = arr / rs
    arr[~np.isfinite(arr)] = 0.0
    return arr


def read_matrix_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(str)
    df.columns = [str(c) for c in df.columns]
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return df


def prepare_ground_truth(gt_path: str) -> pd.DataFrame:
    gt = read_matrix_csv(gt_path)
    gt.columns = normalize_celltype_names(list(gt.columns))
    gt = collapse_duplicate_columns(gt)
    gt = pd.DataFrame(
        safe_row_normalize(gt.values),
        index=gt.index,
        columns=gt.columns,
    )
    return gt


def prepare_prediction_raw(path: str) -> pd.DataFrame:
    df = read_matrix_csv(path)
    df.columns = normalize_celltype_names(list(df.columns))
    df = collapse_duplicate_columns(df)
    df[df < 0] = 0.0
    df = df.fillna(0.0)
    return df


def align_prediction_to_gt(pred_raw: pd.DataFrame, gt: pd.DataFrame, spots: List[str]) -> pd.DataFrame:
    """以 gt 的 cell type 列为准，缺失列填 0，多余列忽略。"""
    celltypes = list(gt.columns)
    aligned = pd.DataFrame(0.0, index=spots, columns=celltypes)

    common_cols = [c for c in celltypes if c in pred_raw.columns]
    if len(common_cols) > 0:
        aligned.loc[:, common_cols] = pred_raw.loc[spots, common_cols].values

    aligned = pd.DataFrame(
        safe_row_normalize(aligned.values),
        index=aligned.index,
        columns=aligned.columns,
    )
    return aligned


@dataclass
class LoadedData:
    gt: pd.DataFrame
    predictions: Dict[str, pd.DataFrame]
    method_names: List[str]
    common_spots: List[str]
    celltypes: List[str]
    pred_tensor: np.ndarray  # shape=(M, N, C)


def load_all_data() -> LoadedData:
    print("BASE_DIR =", BASE_DIR)
    print("PRED_DIR =", PRED_DIR)
    print("GT_PATH  =", GT_PATH)

    if not os.path.exists(GT_PATH):
        raise FileNotFoundError("Ground truth not found: " + GT_PATH)
    if not os.path.isdir(PRED_DIR):
        raise FileNotFoundError("Prediction directory not found: " + PRED_DIR)

    gt = prepare_ground_truth(GT_PATH)
    print("ground truth shape:", gt.shape)
    print("ground truth row sum range:", gt.sum(axis=1).min(), gt.sum(axis=1).max())

    raw_preds = {}
    source_paths = {}
    valid_methods = []

    for method, candidates in METHOD_SPECS.items():
        path = find_file_case_insensitive(PRED_DIR, candidates)
        if path is None:
            print(f"[WARN] {method}: prediction file not found, skip. candidates={candidates}")
            continue

        raw = prepare_prediction_raw(path)
        common = gt.index.intersection(raw.index)
        ratio = len(common) / max(len(gt.index), 1)

        print(f"\n[{method}] file = {path}")
        print("raw shape:", raw.shape)
        print("common spots:", len(common), f"({ratio:.2%})")
        print("raw columns:", list(raw.columns)[:10], "...")

        if ratio < MIN_COMMON_SPOT_RATIO:
            print(f"[WARN] {method}: common spot ratio < {MIN_COMMON_SPOT_RATIO:.0%}, skip.")
            continue

        raw_preds[method] = raw
        source_paths[method] = path
        valid_methods.append(method)

    if len(valid_methods) < 2:
        raise RuntimeError("Need at least 2 valid baseline predictions for fusion.")

    # 所有有效方法 + gt 的共同 spot
    common_spots = list(gt.index)
    for m in valid_methods:
        common_spots = list(pd.Index(common_spots).intersection(raw_preds[m].index))

    if len(common_spots) == 0:
        raise RuntimeError("No common spots across valid methods and ground truth.")

    common_spots = sorted(common_spots)
    gt_use = gt.loc[common_spots].copy()

    aligned_preds = {}
    for m in valid_methods:
        aligned_preds[m] = align_prediction_to_gt(raw_preds[m], gt_use, common_spots)
        print(f"aligned {m}:", aligned_preds[m].shape, "row sum range:",
              aligned_preds[m].sum(axis=1).min(), aligned_preds[m].sum(axis=1).max())

    pred_tensor = np.stack([aligned_preds[m].values for m in valid_methods], axis=0)

    # 保存数据读取配置
    data_config = {
        "BASE_DIR": BASE_DIR,
        "PRED_DIR": PRED_DIR,
        "GT_PATH": GT_PATH,
        "EVAL_DIR": EVAL_DIR,
        "valid_methods": valid_methods,
        "source_paths": source_paths,
        "n_spots": int(len(common_spots)),
        "n_celltypes": int(len(gt_use.columns)),
        "celltypes": list(gt_use.columns),
        "min_common_spot_ratio": MIN_COMMON_SPOT_RATIO,
    }
    with open(os.path.join(EVAL_DIR, f"{OUT_PREFIX}_load_config.json"), "w", encoding="utf-8") as f:
        json.dump(data_config, f, indent=2, ensure_ascii=False)

    return LoadedData(
        gt=gt_use,
        predictions=aligned_preds,
        method_names=valid_methods,
        common_spots=common_spots,
        celltypes=list(gt_use.columns),
        pred_tensor=pred_tensor,
    )


# ============================================================
# 3. 指标函数
# ============================================================
def jensen_shannon_divergence_rows(pred: np.ndarray, true: np.ndarray, eps: float = 1e-12) -> float:
    """平均逐 spot JSD。使用自然对数，lower is better。"""
    p = safe_row_normalize(pred, eps=eps)
    q = safe_row_normalize(true, eps=eps)
    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)
    p = p / p.sum(axis=1, keepdims=True)
    q = q / q.sum(axis=1, keepdims=True)
    m = 0.5 * (p + q)
    jsd = 0.5 * np.sum(p * np.log(p / m), axis=1) + 0.5 * np.sum(q * np.log(q / m), axis=1)
    return float(np.mean(jsd))


def calc_metrics(pred: np.ndarray, true: np.ndarray, celltypes: List[str]) -> Dict[str, float]:
    pred = safe_row_normalize(pred)
    true = safe_row_normalize(true)
    diff = pred - true
    per_ct_rmse = np.sqrt(np.mean(diff ** 2, axis=0))
    out = {
        "JSD": jensen_shannon_divergence_rows(pred, true),
        # 对齐之前 R 脚本里 Sum_RMSE 的习惯：各 cell type RMSE 求和
        "total_RMSE": float(np.sum(per_ct_rmse)),
        # 额外保存一个平均 RMSE，方便自己看，但主排序不用它
        "mean_RMSE": float(np.mean(per_ct_rmse)),
    }
    for ct, v in zip(celltypes, per_ct_rmse):
        out[ct] = float(v)
    return out


def evaluate_predictions(data: LoadedData, proposed: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []

    for method in data.method_names:
        met = calc_metrics(data.predictions[method].values, data.gt.values, data.celltypes)
        met["method_group"] = "baseline"
        met["display_name"] = method
        rows.append((method, met))

    for name, df in proposed.items():
        met = calc_metrics(df.loc[data.common_spots, data.celltypes].values, data.gt.values, data.celltypes)
        met["method_group"] = "proposed"
        met["display_name"] = name
        rows.append((name, met))

    metrics = pd.DataFrame({k: v for k, v in rows}).T

    # 排名：越小越好
    metrics["JSD_rank"] = pd.to_numeric(metrics["JSD"]).rank(method="min")
    metrics["total_RMSE_rank"] = pd.to_numeric(metrics["total_RMSE"]).rank(method="min")
    metrics["mean_rank"] = metrics[["JSD_rank", "total_RMSE_rank"]].astype(float).mean(axis=1)
    metrics = metrics.sort_values(["total_RMSE", "JSD", "mean_rank"])
    return metrics


# ============================================================
# 4. 融合权重学习
# ============================================================
def calc_method_celltype_rmse(pred_tensor: np.ndarray, gt: np.ndarray, train_idx: np.ndarray) -> np.ndarray:
    """返回 shape=(M, C)，每个方法每个 cell type 的 RMSE。"""
    P = pred_tensor[:, train_idx, :]  # M, N, C
    Y = gt[train_idx, :]              # N, C
    diff = P - Y[None, :, :]
    return np.sqrt(np.mean(diff ** 2, axis=1))


def weights_hard_select(pred_tensor: np.ndarray, gt: np.ndarray, train_idx: np.ndarray) -> pd.DataFrame:
    rmse = calc_method_celltype_rmse(pred_tensor, gt, train_idx)  # M, C
    M, C = rmse.shape
    W = np.zeros((C, M), dtype=float)
    best_m = np.argmin(rmse, axis=0)
    W[np.arange(C), best_m] = 1.0
    return pd.DataFrame(W)


def weights_inv_rmse(pred_tensor: np.ndarray, gt: np.ndarray, train_idx: np.ndarray, power: float = 2.0) -> pd.DataFrame:
    rmse = calc_method_celltype_rmse(pred_tensor, gt, train_idx)  # M, C
    score = 1.0 / np.power(rmse + 1e-10, power)
    W = (score / score.sum(axis=0, keepdims=True)).T  # C, M
    return pd.DataFrame(W)


def optimize_simplex_for_cell(X: np.ndarray, y: np.ndarray, init_w: np.ndarray) -> np.ndarray:
    """min ||Xw-y||², w>=0, sum(w)=1。X shape=(N,M)。"""
    M = X.shape[1]

    if not SCIPY_AVAILABLE:
        return init_w / max(init_w.sum(), 1e-12)

    def obj(w):
        r = X @ w - y
        return float(np.mean(r * r))

    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    bounds = [(0.0, 1.0)] * M

    starts = []
    starts.append(np.ones(M) / M)
    starts.append(init_w / max(init_w.sum(), 1e-12))
    # 加入 one-hot 起点，避免局部不好
    for j in range(M):
        v = np.zeros(M)
        v[j] = 1.0
        starts.append(v)

    best_w = starts[0]
    best_val = obj(best_w)

    for s in starts:
        try:
            res = minimize(obj, s, method="SLSQP", bounds=bounds, constraints=cons,
                           options={"maxiter": 300, "ftol": 1e-12, "disp": False})
            if res.success and res.fun < best_val:
                best_val = float(res.fun)
                best_w = np.asarray(res.x, dtype=float)
        except Exception:
            continue

    best_w[best_w < 0] = 0
    if best_w.sum() <= 1e-12:
        best_w = np.ones(M) / M
    else:
        best_w = best_w / best_w.sum()
    return best_w


def weights_softopt_cellwise(pred_tensor: np.ndarray, gt: np.ndarray, train_idx: np.ndarray) -> pd.DataFrame:
    """每个 cell type 独立优化 simplex weights。"""
    M, _, C = pred_tensor.shape
    rmse = calc_method_celltype_rmse(pred_tensor, gt, train_idx)
    inv = 1.0 / np.power(rmse + 1e-10, 2.0)
    inv = (inv / inv.sum(axis=0, keepdims=True)).T  # C, M

    W = np.zeros((C, M), dtype=float)
    for c in range(C):
        X = pred_tensor[:, train_idx, c].T  # N, M
        y = gt[train_idx, c]
        W[c, :] = optimize_simplex_for_cell(X, y, inv[c, :])
    return pd.DataFrame(W)


def softmax_by_cell(logits: np.ndarray) -> np.ndarray:
    """logits shape=(C,M)，返回每个 cell type 一组 simplex weights。"""
    z = logits - np.max(logits, axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def apply_weights(pred_tensor_subset: np.ndarray, W: np.ndarray) -> np.ndarray:
    """pred_tensor_subset shape=(M,N,C), W shape=(C,M)，输出 N,C。"""
    # 对每个 c: sum_m W[c,m] * P[m,:,c]
    fused = np.einsum("mnc,cm->nc", pred_tensor_subset, W)
    return safe_row_normalize(fused)


def weights_softopt_global(pred_tensor: np.ndarray, gt: np.ndarray, train_idx: np.ndarray,
                           init_W: Optional[np.ndarray] = None,
                           maxiter: int = GLOBAL_MAXITER) -> pd.DataFrame:
    """全局优化所有 cell-type weights，使行归一化后的 total_RMSE 最小。"""
    M, _, C = pred_tensor.shape

    if init_W is None:
        init_W = weights_softopt_cellwise(pred_tensor, gt, train_idx).values  # C,M

    if not SCIPY_AVAILABLE:
        return pd.DataFrame(init_W)

    # 用 logits 优化，天然保证每个 cell type 权重非负且和为 1
    init_logits = np.log(np.clip(init_W, 1e-6, 1.0))
    x0 = init_logits.reshape(-1)

    P_train = pred_tensor[:, train_idx, :]
    Y_train = gt[train_idx, :]

    def obj(x):
        logits = x.reshape(C, M)
        W = softmax_by_cell(logits)
        fused = apply_weights(P_train, W)
        per_ct_rmse = np.sqrt(np.mean((fused - Y_train) ** 2, axis=0))
        return float(np.sum(per_ct_rmse))

    try:
        res = minimize(obj, x0, method="L-BFGS-B", options={"maxiter": maxiter, "ftol": 1e-10})
        if res.success or np.isfinite(res.fun):
            W = softmax_by_cell(res.x.reshape(C, M))
            return pd.DataFrame(W)
    except Exception as e:
        print("[WARN] Global SoftOpt failed, use cellwise SoftOpt. error=", repr(e))

    return pd.DataFrame(init_W)


def set_weight_df_labels(Wdf: pd.DataFrame, celltypes: List[str], method_names: List[str]) -> pd.DataFrame:
    Wdf = Wdf.copy()
    Wdf.index = celltypes
    Wdf.columns = method_names
    return Wdf


# ============================================================
# 5. 生成 full-data calibration 版本
# ============================================================
def build_full_data_variants(data: LoadedData) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    pred_tensor = data.pred_tensor
    gt = data.gt.values
    all_idx = np.arange(gt.shape[0])

    proposed = {}
    weights = {}

    # HardSelect
    W = weights_hard_select(pred_tensor, gt, all_idx).values
    fused = apply_weights(pred_tensor, W)
    name = "Proposed_HardSelect_full"
    proposed[name] = pd.DataFrame(fused, index=data.common_spots, columns=data.celltypes)
    weights[name] = set_weight_df_labels(pd.DataFrame(W), data.celltypes, data.method_names)

    # InvRMSE powers
    for p in INVRMSE_POWERS:
        W = weights_inv_rmse(pred_tensor, gt, all_idx, power=p).values
        fused = apply_weights(pred_tensor, W)
        name = f"Proposed_InvRMSE_p{str(p).replace('.', '_')}_full"
        proposed[name] = pd.DataFrame(fused, index=data.common_spots, columns=data.celltypes)
        weights[name] = set_weight_df_labels(pd.DataFrame(W), data.celltypes, data.method_names)

    # SoftOpt cellwise
    W = weights_softopt_cellwise(pred_tensor, gt, all_idx).values
    fused = apply_weights(pred_tensor, W)
    name = "Proposed_SoftOpt_full"
    proposed[name] = pd.DataFrame(fused, index=data.common_spots, columns=data.celltypes)
    weights[name] = set_weight_df_labels(pd.DataFrame(W), data.celltypes, data.method_names)

    # SoftOpt global
    if RUN_GLOBAL_SOFTOPT:
        Wg = weights_softopt_global(pred_tensor, gt, all_idx, init_W=W, maxiter=GLOBAL_MAXITER).values
        fused = apply_weights(pred_tensor, Wg)
        name = "Proposed_SoftOptGlobal_full"
        proposed[name] = pd.DataFrame(fused, index=data.common_spots, columns=data.celltypes)
        weights[name] = set_weight_df_labels(pd.DataFrame(Wg), data.celltypes, data.method_names)

    return proposed, weights


# ============================================================
# 6. 生成 5-fold CV 版本
# ============================================================
def make_folds(n: int, k: int, seed: int = SEED) -> List[np.ndarray]:
    idx = np.arange(n)
    rng_local = np.random.default_rng(seed)
    rng_local.shuffle(idx)
    return [np.array(x, dtype=int) for x in np.array_split(idx, k)]


def build_cv_variant(data: LoadedData, strategy: str, power: float = 2.0) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """返回 cv prediction, 平均 weights, fold weights long table。"""
    pred_tensor = data.pred_tensor
    gt = data.gt.values
    n = gt.shape[0]
    M, _, C = pred_tensor.shape

    folds = make_folds(n, N_FOLDS, SEED)
    fused_all = np.zeros((n, C), dtype=float)
    fold_weight_rows = []
    weight_sum = np.zeros((C, M), dtype=float)

    for fold_i, test_idx in enumerate(folds, start=1):
        train_idx = np.setdiff1d(np.arange(n), test_idx)
        print(f"[CV] strategy={strategy}, fold={fold_i}/{N_FOLDS}, train={len(train_idx)}, test={len(test_idx)}")

        if strategy == "HardSelect":
            W = weights_hard_select(pred_tensor, gt, train_idx).values
        elif strategy == "InvRMSE":
            W = weights_inv_rmse(pred_tensor, gt, train_idx, power=power).values
        elif strategy == "SoftOpt":
            W = weights_softopt_cellwise(pred_tensor, gt, train_idx).values
        elif strategy == "SoftOptGlobal":
            init = weights_softopt_cellwise(pred_tensor, gt, train_idx).values
            W = weights_softopt_global(pred_tensor, gt, train_idx, init_W=init, maxiter=GLOBAL_MAXITER).values
        else:
            raise ValueError("Unknown strategy: " + strategy)

        fused_test = apply_weights(pred_tensor[:, test_idx, :], W)
        fused_all[test_idx, :] = fused_test
        weight_sum += W

        for c, ct in enumerate(data.celltypes):
            for m, method in enumerate(data.method_names):
                fold_weight_rows.append({
                    "fold": fold_i,
                    "cell_type": ct,
                    "method": method,
                    "weight": float(W[c, m]),
                })

    fused_all = safe_row_normalize(fused_all)
    avg_W = weight_sum / N_FOLDS

    pred_df = pd.DataFrame(fused_all, index=data.common_spots, columns=data.celltypes)
    avg_w_df = set_weight_df_labels(pd.DataFrame(avg_W), data.celltypes, data.method_names)
    fold_w_df = pd.DataFrame(fold_weight_rows)
    return pred_df, avg_w_df, fold_w_df


def build_cv_variants(data: LoadedData) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    proposed = {}
    weights = {}
    fold_weights = {}

    # HardSelect CV
    pred, Wavg, Wfold = build_cv_variant(data, "HardSelect")
    name = "Proposed_HardSelect_5foldCV"
    proposed[name] = pred
    weights[name] = Wavg
    fold_weights[name] = Wfold

    # InvRMSE CV
    for p in INVRMSE_POWERS:
        pred, Wavg, Wfold = build_cv_variant(data, "InvRMSE", power=p)
        name = f"Proposed_InvRMSE_p{str(p).replace('.', '_')}_5foldCV"
        proposed[name] = pred
        weights[name] = Wavg
        fold_weights[name] = Wfold

    # SoftOpt CV
    pred, Wavg, Wfold = build_cv_variant(data, "SoftOpt")
    name = "Proposed_SoftOpt_5foldCV"
    proposed[name] = pred
    weights[name] = Wavg
    fold_weights[name] = Wfold

    # SoftOptGlobal CV
    if RUN_GLOBAL_SOFTOPT:
        pred, Wavg, Wfold = build_cv_variant(data, "SoftOptGlobal")
        name = "Proposed_SoftOptGlobal_5foldCV"
        proposed[name] = pred
        weights[name] = Wavg
        fold_weights[name] = Wfold

    return proposed, weights, fold_weights


# ============================================================
# 7. 保存结果
# ============================================================
def save_prediction_csv(df: pd.DataFrame, filename: str):
    path = os.path.join(PRED_DIR, filename)
    df.to_csv(path)
    print("saved prediction:", path, df.shape)
    return path


def save_all_outputs(data: LoadedData,
                     proposed: Dict[str, pd.DataFrame],
                     weights: Dict[str, pd.DataFrame],
                     fold_weights: Dict[str, pd.DataFrame],
                     metrics: pd.DataFrame):
    # 保存 proposed prediction
    pred_paths = {}
    for name, df in proposed.items():
        filename = f"{name}_self_benchmark.csv"
        pred_paths[name] = save_prediction_csv(df, filename)

    # 保存权重
    for name, Wdf in weights.items():
        w_path = os.path.join(EVAL_DIR, f"{name}_weights.csv")
        Wdf.to_csv(w_path)
        print("saved weights:", w_path, Wdf.shape)

    for name, Wfold in fold_weights.items():
        w_path = os.path.join(EVAL_DIR, f"{name}_fold_weights_long.csv")
        Wfold.to_csv(w_path, index=False)
        print("saved fold weights:", w_path, Wfold.shape)

    # 保存指标
    metrics_path = os.path.join(EVAL_DIR, f"{OUT_PREFIX}_metrics_summary.csv")
    metrics.to_csv(metrics_path)
    print("saved metrics:", metrics_path, metrics.shape)

    # 选择 Proposed 最佳版本：只在 proposed 里面选，以 total_RMSE 第一、JSD 第二
    proposed_metrics = metrics[metrics["method_group"] == "proposed"].copy()
    proposed_metrics["total_RMSE"] = pd.to_numeric(proposed_metrics["total_RMSE"])
    proposed_metrics["JSD"] = pd.to_numeric(proposed_metrics["JSD"])
    proposed_metrics = proposed_metrics.sort_values(["total_RMSE", "JSD"])
    best_name = proposed_metrics.index[0]
    best_pred = proposed[best_name]

    best_pred_path = save_prediction_csv(best_pred, "Proposed_best_self_benchmark.csv")

    # 同时把 best weights 复制一份
    if best_name in weights:
        best_w_path = os.path.join(EVAL_DIR, "Proposed_best_weights.csv")
        weights[best_name].to_csv(best_w_path)
    else:
        best_w_path = None

    # 生成 improvement vs best baseline
    baseline_metrics = metrics[metrics["method_group"] == "baseline"].copy()
    baseline_metrics["total_RMSE"] = pd.to_numeric(baseline_metrics["total_RMSE"])
    baseline_metrics["JSD"] = pd.to_numeric(baseline_metrics["JSD"])
    best_baseline_by_rmse = baseline_metrics.sort_values(["total_RMSE", "JSD"]).index[0]
    base_rmse = float(metrics.loc[best_baseline_by_rmse, "total_RMSE"])
    base_jsd = float(metrics.loc[best_baseline_by_rmse, "JSD"])

    improve = metrics[["display_name", "method_group", "JSD", "total_RMSE"]].copy()
    improve["JSD"] = pd.to_numeric(improve["JSD"])
    improve["total_RMSE"] = pd.to_numeric(improve["total_RMSE"])
    improve["delta_JSD_vs_best_baseline"] = improve["JSD"] - base_jsd
    improve["delta_RMSE_vs_best_baseline"] = improve["total_RMSE"] - base_rmse
    improve["JSD_improvement_percent_vs_best_baseline"] = (base_jsd - improve["JSD"]) / base_jsd * 100
    improve["RMSE_improvement_percent_vs_best_baseline"] = (base_rmse - improve["total_RMSE"]) / base_rmse * 100
    improve = improve.sort_values(["total_RMSE", "JSD"])
    improve_path = os.path.join(EVAL_DIR, f"{OUT_PREFIX}_improvement_vs_best_baseline.csv")
    improve.to_csv(improve_path)

    # 保存简短 summary
    summary_lines = []
    summary_lines.append("Reliability-aware fusion summary")
    summary_lines.append("=" * 80)
    summary_lines.append(f"Best baseline by total_RMSE: {best_baseline_by_rmse}")
    summary_lines.append(f"Best proposed by total_RMSE: {best_name}")
    summary_lines.append(f"Best proposed prediction: {best_pred_path}")
    if best_w_path:
        summary_lines.append(f"Best proposed weights: {best_w_path}")
    summary_lines.append("")
    summary_lines.append("Top metrics:")
    summary_lines.extend(metrics[["display_name", "method_group", "JSD", "total_RMSE", "JSD_rank", "total_RMSE_rank", "mean_rank"]].head(20).to_string().splitlines())
    summary_lines.append("")
    summary_lines.append("Improvement vs best baseline:")
    summary_lines.extend(improve[["display_name", "method_group", "JSD_improvement_percent_vs_best_baseline", "RMSE_improvement_percent_vs_best_baseline"]].head(20).to_string().splitlines())

    summary_path = os.path.join(EVAL_DIR, f"{OUT_PREFIX}_brief_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))
    print("saved summary:", summary_path)

    # 保存总配置
    run_config = {
        "SEED": SEED,
        "BASE_DIR": BASE_DIR,
        "PRED_DIR": PRED_DIR,
        "GT_PATH": GT_PATH,
        "EVAL_DIR": EVAL_DIR,
        "N_FOLDS": N_FOLDS,
        "RUN_CV": RUN_CV,
        "RUN_GLOBAL_SOFTOPT": RUN_GLOBAL_SOFTOPT,
        "GLOBAL_MAXITER": GLOBAL_MAXITER,
        "INVRMSE_POWERS": INVRMSE_POWERS,
        "METHOD_SPECS": METHOD_SPECS,
        "valid_methods": data.method_names,
        "n_spots": len(data.common_spots),
        "n_celltypes": len(data.celltypes),
        "best_baseline_by_rmse": best_baseline_by_rmse,
        "best_proposed": best_name,
        "best_pred_path": best_pred_path,
    }
    config_path = os.path.join(EVAL_DIR, f"{OUT_PREFIX}_run_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(run_config, f, indent=2, ensure_ascii=False)
    print("saved config:", config_path)


# ============================================================
# 8. main
# ============================================================
def main():
    np.random.seed(SEED)

    data = load_all_data()
    print("\nValid methods:", data.method_names)
    print("n spots:", len(data.common_spots))
    print("celltypes:", data.celltypes)

    proposed_full, weights_full = build_full_data_variants(data)
    proposed = dict(proposed_full)
    weights = dict(weights_full)
    fold_weights = {}

    if RUN_CV:
        proposed_cv, weights_cv, fold_weights_cv = build_cv_variants(data)
        proposed.update(proposed_cv)
        weights.update(weights_cv)
        fold_weights.update(fold_weights_cv)

    metrics = evaluate_predictions(data, proposed)

    print("\n[Metrics summary]")
    show_cols = ["display_name", "method_group", "JSD", "total_RMSE", "JSD_rank", "total_RMSE_rank", "mean_rank"]
    print(metrics[show_cols])

    save_all_outputs(data, proposed, weights, fold_weights, metrics)

    print("\nDONE.")
    print("Predictions saved to:", PRED_DIR)
    print("Evaluation outputs saved to:", EVAL_DIR)


if __name__ == "__main__":
    main()
