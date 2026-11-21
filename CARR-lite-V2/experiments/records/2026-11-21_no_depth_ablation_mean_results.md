# CARR-lite V2 — no_depth 特征消融：首轮平均指标比较

- 日期：2026-11-21
- 来源：用户在 Windows PowerShell 中执行 pandas 命令，从四份本地 `metrics_by_scenario.csv` 读取 `HGBC_a30` 并按 `base_method, run` 取均值后将日志粘贴到对话。
- 证据等级：**USER_CONSOLE_SUMMARY**（本仓库尚未接收原始 CSV 或独立复算）。
- 记录行数：CARD/full、CARD/no_depth、RCTD/full、RCTD/no_depth 各 52 行，共 208 行固定配置 HGBC_a30 的场景—实验记录。
- 全模型源目录：`D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1`
- 去深度源目录：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1`
- `no_depth` 仅从原特征矩阵去除 `depth_fraction` 列（其余算法路径相同）；脚本变更提交 `f5e3ead23bb122027a5c333d35021f283c2fddac`。

## 终端均值：逐字转录的五位小数

| base_method | run | target_RMSE | target_MAE | balanced_AUPRC | recall_at_10pct_FPR | matrix_RMSE | n_views |
|---|---|---:|---:|---:|---:|---:|---:|
| CARD | full | 0.03137 | 0.02380 | 0.55561 | 0.14690 | 0.09089 | 52 |
| CARD | no_depth | 0.03139 | 0.02381 | 0.55607 | 0.14843 | 0.09089 | 52 |
| RCTD | full | 0.03096 | 0.02375 | 0.55710 | 0.14184 | 0.09004 | 52 |
| RCTD | no_depth | 0.03097 | 0.02377 | 0.55681 | 0.14348 | 0.09004 | 52 |

## 差值（no_depth − full；由五位小数均值计算）

| base_method | Δtarget_RMSE | Δtarget_MAE | Δbalanced_AUPRC | Δrecall@10%FPR | Δmatrix_RMSE |
|---|---:|---:|---:|---:|---:|
| CARD | +0.00002 | +0.00001 | +0.00046 | +0.00153 | 0.00000 |
| RCTD | +0.00001 | +0.00002 | −0.00029 | +0.00164 | 0.00000 |

## 初步解释

在这套相同的 52 个合成场景和固定 `HGBC_a30` 配置下，去除已知深度特征后，目标 RMSE/MAE 均只有小量增加，AUPRC 方向随基础方法不同，召回均微幅增加。这支持**当前协议内对特定深度特征不敏感**的探索性描述；不能据此声明真实数据上等效或统计上无差别。

注意：五位小数经过舍入，`matrix_RMSE` 变化报告为 `0.00000` 只能表示显示精度下未见变化，不能证明完全一致。四个深度共享基础场景，52 个视图不能算 52 个生物学独立重复。

## 下一个计划（尚未执行）

- 依优先队列开展 `no_residual` **特征组消融**，首先 RCTD 的 dry-run；然后 RCTD/CARD 正式执行。
- 最终结果图按 13 个基础场景聚合四深度，报告各组的 paired delta，不进行事后最优超参数挑选。
- 该消融只移除 `residual_projection`、`residual_marker_mean` 输入特征，不能说完全移除残差相关算法结构。
