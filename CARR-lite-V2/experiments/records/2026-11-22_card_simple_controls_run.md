# CARR-lite V2：CARD 简单校准对照正式运行完成（2026-11-22）

## 证据等级与状态

- [USER_WINDOWS_STDOUT / RUN_COMPLETED_AS_REPORTED] 研究者在 Windows 执行 CARD 简单校准基线正式训练及评价，并返回如下终端尾部。GPT 尚未取得实际指标 CSV，不据此宣称性能改善或统计显著。
- CARD 的 `--dry-run` 曾通过 52 模拟场景 / 13 base / 四类类别留出检查。
- RCTD 简单校准对照此前也已有用户终端 `FINISHED 156 result rows`。两法合计预期 **312 评价行**（每法 52 场景×原版/Ridge12/Isotonic1D 三种输出），不是312独立生物重复。

## 用户原样控制台尾部

```text
Completed B12_lowref_ref70_depth_100
Completed B12_lowref_ref70_depth_050
Completed B12_lowref_ref70_depth_025
Completed B12_lowref_ref70_depth_010
Completed B13_lowref_bg8_depth_100
Completed B13_lowref_bg8_depth_050
Completed B13_lowref_bg8_depth_025
Completed B13_lowref_bg8_depth_010
FINISHED 156 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\CARD
```

## 本地结果位置

- `D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\RCTD\metrics_by_scenario.csv`
- `D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\CARD\metrics_by_scenario.csv`
- 对应四类严格留出 CARR 旧结果：`D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\{RCTD,CARD}\metrics_by_scenario.csv`。

## 下一步唯一人工操作（只读）

同一 `base_method`、`scenario_id` 对齐两份输出；先要求：
1. 简单基线 312 行，6组×52；完整CARR 520行，10组×52，五指标无缺失；
2. 原版`Original_RCTD`/`Original_CARD`在两批中的五指标一致（包括依赖随机种子的 balanced AUPRC）；不一致时不得直接比较；
3. 固定 `HGBC_a30`（不后验挑 alpha）与 `Ridge12`、`Isotonic1D`、`AbundanceOnly` 公平比较五指标总体均值，随后按13个基础模拟场景聚合四深度再进行配对比较；
4. CARD 在严格类别留出下相较 Original 检测 AUPRC 与 Recall 变差的负结果必须保留。

无新增空间预测点位图；不重复训练。该步骤只汇总现有CSV。
