# CARR-lite V2 × CARD：52 场景跨基础方法实验记录

- 日期：2026-11-21（用户提供的 Windows PowerShell 日志）
- 状态：**RUN_LOG_CONFIRMED**（终端确认；本地原始 metrics CSV 仍未读取/归档）
- 方法：CARD 基础预测 + CARR-lite V2 在 13 个基础场景上留一（每个基础场景的 4 个深度全部留出）
- 脚本：[`../cross_method_carr_v2.py`](../cross_method_carr_v2.py)，首次提交 `4583fa605bd175779c91a4ba665a0d6dcc1fd7d2`
- 本地输出：`D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\CARD`

## 用户反馈的实际执行证据

1. `--method CARD --dry-run` 输出：`INPUT CHECK PASS: CARD 52 scenario views`；`DRY RUN PASS — no files written`。
2. 正式执行日志后段包含 B09–B13 全部所列深度场景的 `Completed`，并显示：
   ```text
   FINISHED 260 result rows
   OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\CARD
   ```
3. 从脚本结构推断，一条方法—场景结果包含原始 CARD、AbundanceOnly、HGBC_a15/a30/a50；`52 × 5 = 260`。
4. **尚未收到 CSV 具体数值；不能据“完成”推断 CARR 有提升。**

## 现在可以开展的下一项工作

同时读取 `RCTD/metrics_by_scenario.csv` 和 `CARD/metrics_by_scenario.csv`，汇总 `matrix_RMSE`、`target_RMSE`、`target_MAE`、`balanced_AUPRC`、`recall_at_10pct_FPR`。第一轮仅作**各场景描述性均值**；随后按 13 个基础场景制作配对变化表，避免把四种深度当四个独立生物学重复。

不在本阶段启动额外全面审计。原始数据、训练代码和旧结果不覆盖。
