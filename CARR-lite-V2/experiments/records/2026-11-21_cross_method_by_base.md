# CARR-lite V2：按基础场景的配对改变量（用户终端结果）

- 日期：2026-11-21
- 来源：研究者本地 PowerShell `python -c` 读取 `RCTD/metrics_by_scenario.csv`、`CARD/metrics_by_scenario.csv` 之后打印的结果。
- 对比：`HGBC_a30 - Original`，先对每个 `held_out_base` 内四种测序深度的指标取均值。
- 状态：**USER_CONSOLE_SUMMARY**；GitHub 尚未收到两份原始 520 行 CSV，仅记录本轮可见的分组计数和部分行。用户消息开头的 CARD 结果已截断，**不能补造缺失 12 行**。

## 两种基础方法都得到的分组结论

| 基础方法 | Target RMSE 下降的基础场景 | Balanced AUPRC 上升的基础场景 | AUPRC 未上升的场景 |
|---|---:|---:|---:|
| RCTD | **13 / 13** | **10 / 13** | 3 / 13 |
| CARD | **13 / 13** | **9 / 13** | 4 / 13 |

这里 `target_RMSE` 越小越好，`balanced_AUPRC` 越大越好。差值为 CARR a30 减去原方法；因此负 RMSE 差值、正 AUPRC 差值表示改善。

**注意**：13 个基础场景是模拟设计中的成组配置，不等同于 13 个独立供体或生物学重复；计数是描述性指标，不等于统计显著性。

## 本次可见的 RCTD 逐基础场景数值（终端打印，精度 5 位）

| base | ΔTarget RMSE | ΔBalanced AUPRC |
|---|---:|---:|
| B01_stable_bg3 | -0.04103 | +0.01330 |
| B02_stable_bg5 | -0.03662 | +0.04376 |
| B03_stable_bg8 | -0.03430 | +0.04213 |
| B04_stable_bg12 | -0.01849 | +0.01695 |
| B05_medium_ref50 | -0.00739 | +0.02206 |
| B06_medium_ref70 | -0.01261 | +0.00115 |
| B07_medium_ref85 | -0.01871 | +0.01511 |
| B08_confusable_bg3 | -0.03616 | +0.01416 |
| B09_confusable_bg5 | -0.02912 | -0.00180 |
| B10_confusable_bg8 | -0.02684 | -0.00511 |
| B11_lowref_ref50 | -0.02309 | +0.00394 |
| B12_lowref_ref70 | -0.04418 | +0.00094 |
| B13_lowref_bg8 | -0.02148 | -0.00696 |

## 下一项扩充（代码已准备，尚未运行）

已更新 [`cross_method_carr_v2.py`](../cross_method_carr_v2.py)，新增 `--ablation` 选项；默认 `none` 路径保持原实验逻辑不变。新脚本支持：

- `no_depth`: 删除第 12 项 `depth_fraction`；
- `no_residual`: 删除两个残差特征；
- `no_confusion_features`: 删除混淆相关特征，但仍使用原算法的局部混淆校正约束；
- `no_marker_features`: 删除标记基因相关特征，但不移除原有参考细胞/混淆机制。

这只是**输入特征消融**，不能写成整个存在分支/混淆机制的结构消融。独立新目录输出，默认不覆盖历史 RCTD/CARD 结果。

准备按以下次序在用户 Windows 本机操作：`git pull --ff-only` → `--method RCTD --ablation no_depth --dry-run` → `RCTD no_depth` 正式实验 → `CARD no_depth`。执行前后记录脚本 Git SHA，绝不提前填结果。
