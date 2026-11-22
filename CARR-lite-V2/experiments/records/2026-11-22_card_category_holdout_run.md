# 2026-11-22 CARR-lite V2 严格类别留出 — CARD 正式运行完成（用户 Windows 日志）

## 当前状态与证据

- **USER_WINDOWS_STDOUT / RUN_COMPLETED_AS_REPORTED**：研究者在 Windows 本地运行正式 CARD 类别留出实验，并提供了脚本运行尾部日志；没有提供原始指标 CSV，所以目前只有运行成功证据，没有性能结论。
- 前序同协议 CARD `--dry-run` 已通过 52 场景 / 13 个 base / 四类整类留出检查。
- RCTD 同协议此前用户返回了 `FINISHED 260 result rows`；至此 RCTD/CARD 两组各 260 行，总计预期 520 评价行，但尚未读取实际 CSV 验证各行指标。
- 类别留出把 stable、medium、confusable、lowref 各类整体留出，测试视图分别 16、12、12、12 个；这不构成独立生物学重复或外部真实数据验证。

## 用户原样日志尾部

```text
Completed B12_lowref_ref70_depth_050
Completed B12_lowref_ref70_depth_025
Completed B12_lowref_ref70_depth_010
Completed B13_lowref_bg8_depth_100
Completed B13_lowref_bg8_depth_050
Completed B13_lowref_bg8_depth_025
Completed B13_lowref_bg8_depth_010
FINISHED 260 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\CARD
```

## 本地结果

- `D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\RCTD\metrics_by_scenario.csv`
- `D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\CARD\metrics_by_scenario.csv`

## 下一步唯一人工操作

研究者运行一条只读 PowerShell/Python 命令，读取这两份 CSV，核验 RCTD/CARD 各 260 行，每基础方法五种方法各 52 行，报告 `target_RMSE`、`target_MAE`、`balanced_AUPRC`、`recall_at_10pct_FPR`、`matrix_RMSE` 的总体均值，并按 `held_out_category` 汇总 Original 与 `HGBC_a30`。先看真实输出再决定与先前留 base 协议的具体比较；不重跑旧消融，不做空间点位图。
