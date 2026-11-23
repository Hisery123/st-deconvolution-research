# 2026-11-23 CTW-RF EnDecon融合核心Python移植对照：正式运行完成

## 研究者Windows原始终端记录

[USER_WINDOWS_STDOUT / RUN_LOG_CONFIRMED] 用户在完成`--dry-run`输入和算法自检后，本地运行：
`python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_endecon_aggregation_batch.py" --run`。

```text
ALGORITHM SELFTEST PASS
INPUT CHECK PASS 2000 spots 19 cell types 6 methods
CTW REFERENCE PASS 3 seeds x 3 method pools
DESIGN 3 pools x 3 unsupervised ensemble controls = 9 rows
COMPLETED strong2 EnDecon JSD 0.098996 RMSE 0.056752 iterations 3 converged True
COMPLETED expanded4 EnDecon JSD 0.11934 RMSE 0.051988 iterations 3 converged True
COMPLETED full6 EnDecon JSD 0.233707 RMSE 0.073754 iterations 3 converged True
BATCH FINISHED 3 method pools x 3 ensemble variants; 18 CTW reference comparisons
OUTPUT D:\Research\STdeconv_benchmark\results\CTWRF_EnDecon_aggregation_20261122_v1
```

## 与历史CTW SoftOpt同池对照的描述性比较

前一批用户终端CSV数据显示CTW SoftOpt在同一2000伪spot上的三种seed均值：
- strong2 CTW JSD 0.114850, matrix_RMSE 0.052449；本轮EnDecon聚合JSD 0.098996, RMSE 0.056752。因此**EnDecon在该池JSD较好，CTW在该池RMSE较好**，不可声称CTW所有设置全面领先。
- expanded4 CTW JSD 0.110677, RMSE 0.044521；EnDecon聚合JSD 0.119340, RMSE 0.051988。
- full6 CTW JSD 0.101723, RMSE 0.041453；EnDecon聚合JSD 0.233707, RMSE 0.073754，表现明显差异，但**需读权重确认原因**，不能归因于失效/偏差机制而无证据。
- 3种seed CV配对并不使EnDecon单次无监督聚合变成独立三次重复；EnDecon不使用真值，但允许全2000目标spot预测学习全局方法权重（transductive）；CTW使用fold训练真值拟合并在折外评估。这两者属于不同监督设置。
- `iterations 3 converged True`仅表示本Python移植按其目标变化阈值收敛，不是“原作者完整R流程已被数值验证”。

## 输出证据边界

- [RUN_LOG_CONFIRMED] 已确认三个方法池都完成、9个变体指标行/18项seed参照比较在日志显示批处理完成。
- [PENDING_READ] `ensemble_metrics_by_pool.csv`尚未读出coordinate_median和equal_mean实际指标。
- [PENDING_READ] `endecon_weights_by_pool.csv`尚未读出各基线方法权重。**强2池JSD 0.098996近似cell2location历史基线JSD 0.098996，只是权重集中假设，绝不可当作确认。**
- [PENDING_READ] `endecon_diagnostics_by_pool.csv`尚未读出lambda、计时和收敛记录。
- 下一步用户Windows用**一条只读PowerShell Python命令**打印上述三CSV关键行与列，确认EnDecon融合退化与对照结果，再规划跨数据集实验。
- 已检查作者github仓库`Zhangxf-ccnu/EnDecon`的`R/EnDeconv.R`融合阶段`solve_ensemble`，本实验仅移植该阶段，未直接执行官方R包，也没有重做作者多模型全流程；加权中位数半权重边界的tie规则可能有细节差异，结果必须标为Python port。
- 当前用户要求继续原计划批量做完实验、最终由Claude集中审计。仍不可忽视必要的实验标签/证据界线，不进行额外重复运行或覆盖数据。
