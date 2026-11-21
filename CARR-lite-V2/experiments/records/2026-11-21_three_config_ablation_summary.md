# CARR-lite V2：Full / No_depth / No_residual（RCTD、CARD）

- 日期：2026-11-21
- 证据等级：**USER_CONSOLE_SUMMARY**；用户 Windows 端通过 pandas 读取本地六份 `metrics_by_scenario.csv`，返回下列汇总表。仓库仅归档终端转录值，未读取原始本地 CSV。
- CARD `no_residual` 先前目标路径存在，用户只读检查显示 52 场景目录、260 行指标和 `run_config.json`。本轮进一步从 JSON 验证 `base_method=CARD`、`ablation=no_residual`，避免误用旧目录；用户本轮被 `FileExistsError` 拦截的再次执行**没有训练**。
- 固定变体：**`HGBC_a30`**；RCTD / CARD 两种基础方法 × Full / No_depth / No_residual 三配置，每配置 52 条记录，共 312 条过滤后的方法—场景结果。四种测序深度共享基础场景，不是独立生物学重复。
- 数字来自用户终端输出的五位小数均值；另存 [机器可读终端转录 CSV](2026-11-21_three_config_console_means.csv)。

## 原始终端摘要（5 位小数）

| base_method | variant | target_RMSE | target_MAE | balanced_AUPRC | recall_at_10pct_FPR | matrix_RMSE | n |
|---|---|---:|---:|---:|---:|---:|---:|
| CARD | Full | 0.03137 | 0.02380 | 0.55561 | 0.14690 | 0.09089 | 52 |
| CARD | No_depth | 0.03139 | 0.02381 | 0.55607 | 0.14843 | 0.09089 | 52 |
| CARD | No_residual | 0.03163 | 0.02392 | 0.55421 | 0.14092 | 0.09089 | 52 |
| RCTD | Full | 0.03096 | 0.02375 | 0.55710 | 0.14184 | 0.09004 | 52 |
| RCTD | No_depth | 0.03097 | 0.02377 | 0.55681 | 0.14348 | 0.09004 | 52 |
| RCTD | No_residual | 0.03114 | 0.02383 | 0.55728 | 0.14181 | 0.09005 | 52 |

## 事先固定 HGBC_a30 后的描述性效应（相对 Full）

- CARD No_depth：Target RMSE +0.00002（约 +0.06%），Target MAE +0.00001，AUPRC +0.00046，Recall +0.00153。
- RCTD No_depth：Target RMSE +0.00001（约 +0.03%），Target MAE +0.00002，AUPRC −0.00029，Recall +0.00164。
- CARD No_residual：Target RMSE +0.00026（约 +0.83%），Target MAE +0.00012，AUPRC −0.00140，Recall −0.00598。
- RCTD No_residual：Target RMSE +0.00018（约 +0.58%），Target MAE +0.00008，AUPRC +0.00018，Recall −0.00003。

在本模拟协议的**平均 Target RMSE** 上，去残差两个特征所产生的误差增加比去已知深度特征更大；但 RCTD 的 AUPRC 在 no_residual 略升，效果并非所有指标方向一致。

**范围限制：** 此处只是特征输入消融 `residual_projection` / `residual_marker_mean`，不是关闭完整残差修正模块。当前未做按 13 个基础场景的置信区间、配对检验，不能断言统计显著或不同平台等效。精度仅 5 位小数，表中相等可能只是舍入。

## 后续执行安排（未运行）

继续 `no_confusion_features` 特征组消融，先 RCTD `--dry-run` 再运行；随后 CARD 同样运行。保持独立输出目录，不添加 `--force`。最终统一汇总所有预先声明的配置，包括负结果。
