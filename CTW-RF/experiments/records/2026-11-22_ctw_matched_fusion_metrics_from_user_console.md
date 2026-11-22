# 2026-11-22 CTW-RF matched-fold对照：用户本机CSV数值汇总

## 证据

[USER_WINDOWS_CSV_SUMMARY] 研究者在Windows本地通过pandas只读读取以下三个CSV：

- `D:\Research\STdeconv_benchmark\results\CTWRF_matched_fusion_20261122_v1\summary_metrics_by_seed_pool.csv`
- `paired_differences_by_seed_pool.csv`
- `fit_runtime_by_fold.csv`

本记录转录用户终端打印数值；原始CSV内容尚未整体上传给本助手或由本助手逐行复算。此前用户原始run日志`BATCH FINISHED 9 matched seed-pool experiments; method summaries 81`，各配置optimizer fallback为0。

## CTW SoftOpt对Global Stacking的三seed均值

| pool | method | JSD | matrix_RMSE | aggregated_celltype_RMSE |
|---|---|---:|---:|---:|
| expanded4 | CTW_SoftOpt | 0.110677 | 0.044521 | 0.774836 |
| expanded4 | GlobalStacking | 0.113403 | 0.049586 | 0.876432 |
| full6 | CTW_SoftOpt | 0.101723 | 0.041453 | 0.725489 |
| full6 | GlobalStacking | 0.113531 | 0.048966 | 0.867231 |
| strong2 | CTW_SoftOpt | 0.114850 | 0.052449 | 0.897847 |
| strong2 | GlobalStacking | 0.116177 | 0.052691 | 0.901901 |

- full6：CTW相对GlobalStacking，JSD降低(0.113531−0.101723)/0.113531 ≈ 10.4%，matrixRMSE降低(0.048966−0.041453)/0.048966 ≈ 15.3%，aggregated celltype RMSE由0.867231降至0.725489。
- 在3×3=9组匹配seed/pool设置下，CTW对GlobalStacking的JSD与matrixRMSE均改善9/9；**同一份数据不同随机划分，非9个独立生物重复**。

## 9配对设置下的改善方向计数

| versus | n | JSD_wins | RMSE_wins | mean_delta_JSD (CTW−control) | mean_delta_matrix_RMSE |
|---|---:|---:|---:|---:|---:|
| CTW_HardSelect | 9 | 9 | 9 | −0.010393 | −0.003130 |
| CTW_InvRMSE_p2 | 9 | 6 | 9 | −0.005738 | −0.001828 |
| EqualWeight | 9 | 6 | 9 | −0.026782 | −0.008489 |
| GlobalStacking | 9 | 9 | 9 | −0.005287 | −0.004273 |

- CTW SoftOpt JSD对InvRMSE_p2、EqualWeight各只有6/9改善；不得称全部方法/指标一致领先。
- 所有mean delta对9组技术相关设置的描述性平均，不应据此做独立样本显著性推断。

## 45次折内拟合时间

| method | n fits | mean_seconds | sum_seconds |
|---|---:|---:|---:|
| CTW_HardSelect |45|0.001|0.066|
| CTW_InvRMSE_p2 |45|0.001|0.063|
| CTW_SoftOpt |45|0.331|14.904|
| GlobalStacking |45|0.015|0.671|

- 各优化方法的拟合阶段耗时；不是整个分析流程wall time，也不是包含原始基础反卷积器拟合的end-to-end runtime。CTW SoftOpt约为GlobalStacking 22×的拟合用时，但绝对时长仍低。提供对比时注明不同优化问题和模型复杂度。

## 接下来

- 用户要求先一批批完成原计划扩充，不再逐步插入大范围审计；最终交Claude统一核查。不可擅报尚未执行的实验结果。
- 经检索已核实最接近公开集成工作之一：Tu et al.《EnDecon: cell type deconvolution of spatially resolved transcriptomics data via ensemble learning》，Bioinformatics 39(1), btac825, DOI 10.1093/bioinformatics/btac825；作者实现位于`Zhangxf-ccnu/EnDecon`的`R/EnDeconv.R`第1251–1309行，聚合核心为加权中位数+L1距离权重熵正则交替优化，区别于简单加权平均。若为Python轻量改写必须明确称为作者算法port，尚非作者原生R包运行。
