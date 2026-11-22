# 2026-11-22 CARR-lite V2 四类严格留出 — RCTD/CARD 指标检查及初步比较

## 证据等级

- **USER_WINDOWS_STDOUT**：用户在 Windows 读取 `D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\{RCTD,CARD}\metrics_by_scenario.csv` 后提供原始终端输出。
- [CHECK PASS] `520 rows, 10 groups, 52 rows each`；五项指标均非缺失。
- **原始 520 行 CSV 尚未上传至 ChatGPT/GitHub**。以下是用户终端显示五位小数的描述性均值，暂未逐行独立复算，不能声称统计显著。
- 52 views = 13 模拟基础场景 ×4 受控测序深度；4 折整类别留出仍不是独立真实生物样本。

## 严格类别留出 10 组五指标均值（USER_STDOUT）

```csv
base_method,method,target_RMSE,target_MAE,balanced_AUPRC,recall_at_10pct_FPR,matrix_RMSE
CARD,AbundanceOnly,0.03305,0.02526,0.54489,0.13914,0.09095
CARD,HGBC_a15,0.03298,0.02501,0.54514,0.13857,0.09093
CARD,HGBC_a30,0.03297,0.02481,0.54521,0.13832,0.09092
CARD,HGBC_a50,0.03308,0.02465,0.54554,0.13682,0.09090
CARD,Original_CARD,0.03720,0.02604,0.55189,0.14612,0.09094
RCTD,AbundanceOnly,0.03228,0.02485,0.55536,0.13967,0.09003
RCTD,HGBC_a15,0.03227,0.02460,0.55577,0.14060,0.09007
RCTD,HGBC_a30,0.03236,0.02439,0.55619,0.14103,0.09012
RCTD,HGBC_a50,0.03260,0.02420,0.55687,0.14345,0.09018
RCTD,Original_RCTD,0.05789,0.03953,0.54487,0.12454,0.08986
```

## 四类别：原版 vs HGBC_a30 的 Target RMSE / Balanced AUPRC

```csv
base_method,held_out_category,method,target_RMSE,balanced_AUPRC
CARD,confusable,HGBC_a30,0.03591,0.50924
CARD,confusable,Original_CARD,0.04018,0.50847
CARD,lowref,HGBC_a30,0.03626,0.51773
CARD,lowref,Original_CARD,0.03906,0.50817
CARD,medium,HGBC_a30,0.03109,0.59406
CARD,medium,Original_CARD,0.03398,0.59400
CARD,stable,HGBC_a30,0.02971,0.55615
CARD,stable,Original_CARD,0.03599,0.58568
RCTD,confusable,HGBC_a30,0.03614,0.51844
RCTD,confusable,Original_RCTD,0.06544,0.52024
RCTD,lowref,HGBC_a30,0.03610,0.52000
RCTD,lowref,Original_RCTD,0.06511,0.52098
RCTD,medium,HGBC_a30,0.03100,0.56364
RCTD,medium,Original_RCTD,0.04156,0.56470
RCTD,stable,HGBC_a30,0.02772,0.60607
RCTD,stable,Original_RCTD,0.05906,0.56639
```

## 和旧的逐基础场景留出对比（只用 HGBC_a30）

- CARD：Target RMSE `0.03137→0.03297`（升 `0.00160`、约 `5.10%`），Balanced AUPRC `0.55561→0.54521`（降 `0.01040`）。
- RCTD：Target RMSE `0.03096→0.03236`（升 `0.00140`、约 `4.52%`），Balanced AUPRC `0.55710→0.55619`（降 `0.00091`）。
- 严格划分下相对原版：CARD HGBC_a30 Target RMSE `0.03720→0.03297`，降 `11.37%`；AUPRC `0.55189→0.54521` **下降**；Recall `0.14612→0.13832` **下降**。RCTD Target RMSE `0.05789→0.03236`，降 `44.10%`；AUPRC `0.54487→0.55619` **上升**、Recall `0.12454→0.14103` **上升**，matrix_RMSE `0.08986→0.09012` **略变差**。
- CARD stable 整类留出 AUPRC `0.58568→0.55615`，差 `-0.02953`，是值得解释的负结果；CARD lowref `0.50817→0.51773`，有提升。不能据此已经证明“过度校准”；只是潜在解释。

## 统计与分析边界

- 以上仅比较五位小数的无权场景平均数。新旧拆分结果来自相同 52 个场景视图，需要进一步**按相同 `scenario_id` 配对**，并优先将4种depth归并至13个基础场景后汇总，防止伪重复。
- 用户本地旧结果：`D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\{RCTD,CARD}\metrics_by_scenario.csv`。
- 用户本地新结果：`D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\{RCTD,CARD}\metrics_by_scenario.csv`。
- **下一个唯一本地操作**：只读配对 52 场景的同一方法 `HGBC_a30` 新旧指标，按基础场景先平均4深度，再给出各13 base变化与按类别差异；不发散新实验，不补空间点位图。
