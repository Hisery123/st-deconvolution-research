# 2026-11-22 CARR-lite V2 12任务补实验统一批处理：正式运行完成

## 证据来源

- [USER_WINDOWS_STDOUT] 研究者在本地执行 `CARR-lite-V2/experiments/carr_pending_experiments_batch.py --run` 后提供终端结束日志：

```text
logistic_threshold CARD TRAINING FOLD 3 confusable train 40 test 12
logistic_threshold CARD TRAINING FOLD 4 lowref train 40 test 12
logistic_threshold CARD Completed B13_lowref_bg8_depth_100
logistic_threshold CARD Completed B13_lowref_bg8_depth_050
logistic_threshold CARD Completed B13_lowref_bg8_depth_025
logistic_threshold CARD Completed B13_lowref_bg8_depth_010
logistic_threshold CARD FINISHED 156 result rows
logistic_threshold CARD OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_pending_batch_20261122_v1\logistic_threshold\CARD
DONE logistic_threshold CARD elapsed_seconds 89.93
BATCH FINISHED 12 jobs
METRICS D:\Research\STdeconv_benchmark\results\CARRliteV2_pending_batch_20261122_v1\batch_metric_means.csv
STATUS D:\Research\STdeconv_benchmark\results\CARRliteV2_pending_batch_20261122_v1\batch_run_status.csv
```

- 此前同一研究者执行该批的 `--dry-run`，12/12任务均标记NEW、四项输入检查通过、`BATCH PREFLIGHT PASS: 12 jobs`。
- [RUN_LOG_CONFIRMED] 调度器仅在全部子任务返回完成、内部检查通过后输出`BATCH FINISHED 12 jobs`。本批无证据表明有跳过任务；但必须实际读取`batch_run_status.csv`才可独立确认每个子任务状态及耗时。
- [METRICS_NOT_YET_READ] 终端只提供输出路径，没有本批各指标值，**不得臆造效果方向、统计显著性或最优参数**。预期10个CARR敏感性/去深度实验×260行 + 2个简单对照×156行 = **2912行**，该总数来自设计，非用户已打印合计。完整数值仅存于Windows本机结果CSV。

## 完成范围

- RCTD / CARD各：marker_k=20、80，confusion_k=1、5，在四类别留出下训练的no_depth，以及LogisticPresence12/Threshold1D简单后校准对照；共12个任务。历史Full/Ridge12/Isotonic1D和原方法不用重跑。
- 脚本中嵌套52个模拟视图、四类group holdout；不是52个独立生物学重复。
- 保存完整原始子任务日志`...\logs`、状态`batch_run_status.csv`、指标均值`batch_metric_means.csv`；保持负结果。

## 下一步：优先继续推进CTW-RF实验（用户要求加快、审计后置）

- CTW 36配置批处理脚本：`CTW-RF/experiments/ctw_stacking_sensitivity_batch.py`，已在GitHub并已由用户先前成功git pull同步（本次尚未Windows dry-run）。
- Windows用户下一条只读命令：`python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_stacking_sensitivity_batch.py" --dry-run`。
- 若显示`INPUT CHECK PASS`、`DESIGN 3 seeds x 3 method pools x 4 budgets = 36 configurations`和`DRY RUN PASS — no files written`，再单独发`--run`启动批量计算。
- 这批只验证**GlobalStacking 对照**的随机拆分、方法池、校准量敏感性，绝不谎称CTW-RF Proposed_CV同折重跑。
- 本地新CARR指标仍需稍后用户用一条只读命令读出，形成Results/敏感性表格；用户已要求优先完成所有批次后再集中审计。
