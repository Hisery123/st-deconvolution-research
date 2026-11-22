# 2026-11-22 CARR-lite V2 与简单校准器公平比较（四类别严格留出）

## 证据等级及一致性检查

- [USER_WINDOWS_STDOUT] 研究者在 Windows 本地只读以下四份 CSV：
  - `D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\RCTD\metrics_by_scenario.csv`
  - `D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\CARD\metrics_by_scenario.csv`
  - `D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\RCTD\metrics_by_scenario.csv`
  - `D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\CARD\metrics_by_scenario.csv`
- 控制台：`CHECK PASS: 312 simple rows, 520 CARR rows`、`ORIGINAL PARITY PASS`。两批中的 `Original_RCTD`/`Original_CARD` 对应场景的五指标已按method/scenario/base_method排序并检查一致，`np.allclose(atol=1e-12,rtol=0)`。
- 记录的是研究者终端五位小数均值；本次尚未上传完整CSV并逐行独立复算。52视图来自13个基础模拟场景×4个深度，不是52个独立生物学重复。
- 固定CARR融合 `HGBC_a30`，不从HGBC_a15/a30/a50后验选择最好结果。其他校准方案：Ridge12、Isotonic1D、AbundanceOnly；底层原方法也是对照。

## 研究者终端整体均值（五位小数）

```csv
base_method,method,target_RMSE,target_MAE,balanced_AUPRC,recall_at_10pct_FPR,matrix_RMSE
CARD,AbundanceOnly,0.03305,0.02526,0.54489,0.13914,0.09095
CARD,HGBC_a30,0.03297,0.02481,0.54521,0.13832,0.09092
CARD,Isotonic1D,0.03316,0.02650,0.54839,0.13875,0.09097
CARD,Original_CARD,0.03720,0.02604,0.55189,0.14612,0.09094
CARD,Ridge12,0.03280,0.02576,0.54383,0.12845,0.09098
RCTD,AbundanceOnly,0.03228,0.02485,0.55536,0.13967,0.09003
RCTD,HGBC_a30,0.03236,0.02439,0.55619,0.14103,0.09012
RCTD,Isotonic1D,0.03320,0.02666,0.54062,0.10702,0.08999
RCTD,Original_RCTD,0.05789,0.03953,0.54487,0.12454,0.08986
RCTD,Ridge12,0.03311,0.02646,0.54719,0.13775,0.08998
```

## 必须保留的公平解释与负结果

1. **RCTD**：HGBC_a30在Target RMSE及AUPRC上均优于Ridge12和Isotonic1D；Ridge12 RMSE 0.03311→HGBC 0.03236（差-0.00075），AUPRC 0.54719→0.55619（+0.00900）。然而**AbundanceOnly 的目标RMSE 0.03228 更低于 HGBC_a30 0.03236**；CARR的Matrix RMSE 0.09012略高于Original_RCTD的0.08986，不可声称全指标更好。
2. **CARD**：Ridge12的Target RMSE 0.03280低于HGBC_a30的0.03297（幅度很小）；Isotonic1D AUPRC 0.54839高于HGBC_a30 0.54521，**原始CARD AUPRC 0.55189、Recall@10%FPR 0.14612均高于所有简单校准与CARR**。HGBC_a30在这五个CARD方法/校准器中Target MAE 0.02481最低、Matrix RMSE 0.09092最低，但不能宣称检测性能改善。
3. `Ridge12` 使用12个模型输入，包括仅受控模拟可知的 `depth_fraction`，与当前 HGBC_a30 同属于模拟协议；`Isotonic1D` 只用一维目标预测。简单基线能否泛化到真实数据尚待验证。
4. 以上是描述性均值，没有13-base配对效应的完整方向数量、置信区间、独立真实数据验证或显著性检验；不能断言任一0.0001级差异可重复、显著或具实践重要性。
5. 本结果是对“复杂三分支是否必要”的实质检验，不应后验删除不利基线或以改用 `HGBC_a50` 等方式选择最佳测试结果。

## 下一步唯一人工分析步骤

从同一四份本地CSV挑出 `Original_*`、`Ridge12`、`Isotonic1D`、`AbundanceOnly`、`HGBC_a30`，按 `base_method/held_out_base` 聚合每四种depth，计算CARR相较每个基线 Target RMSE/AUPRC 差与改善base个数，检查13个基础模拟场景上结论是否一致。仅只读现有结果，不重新训练、不补空间预测地图。
