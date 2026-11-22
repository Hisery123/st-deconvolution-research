# 2026-11-22 CTW-RF 主方法与全局stacking同折对照：9配置全部成功

## 证据与实验配置

- [USER_WINDOWS_STDOUT / RUN_LOG_CONFIRMED] 用户Windows在同步到`6f9d563`之后，先运行`ctw_matched_fusion_comparisons_batch.py --dry-run`：
  ```text
  INPUT CHECK PASS 2000 spots 19 cell types 6 base methods
  DESIGN 3 seeds x 3 method pools = 9 matched 5-fold experiments
  DRY RUN PASS — no files written
  ```
- 后运行`python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_matched_fusion_comparisons_batch.py" --run`。每个配置在同一五折下比较历史CTW SoftOpt实现、GlobalStacking、EqualWeight、HardSelect、InvRMSE_p2与单方法；使用已有2000个伪spot /19类 /六基础方法预测。输出新目录，不覆盖旧结果。
- 本轮当前仅得到控制台摘要JSD；**尚未直接读取新输出CSV中的matrix_RMSE、aggregated_celltype_RMSE、逐折差值、拟合耗时**。不推断这些指标的方向或显著性。

## 用户Windows终端原始尾部输出

```text
INPUT CHECK PASS 2000 spots 19 cell types 6 base methods
DESIGN 3 seeds x 3 method pools = 9 matched 5-fold experiments
COMPLETED seed 2026 pool strong2 CTW_SoftOpt 0.114873 GlobalStacking 0.116179 optimizer_fallback_total 0
COMPLETED seed 2026 pool expanded4 CTW_SoftOpt 0.11069 GlobalStacking 0.113395 optimizer_fallback_total 0
COMPLETED seed 2026 pool full6 CTW_SoftOpt 0.101752 GlobalStacking 0.113543 optimizer_fallback_total 0
COMPLETED seed 2027 pool strong2 CTW_SoftOpt 0.114838 GlobalStacking 0.116167 optimizer_fallback_total 0
COMPLETED seed 2027 pool expanded4 CTW_SoftOpt 0.110651 GlobalStacking 0.113383 optimizer_fallback_total 0
COMPLETED seed 2027 pool full6 CTW_SoftOpt 0.10169 GlobalStacking 0.113507 optimizer_fallback_total 0
COMPLETED seed 2028 pool strong2 CTW_SoftOpt 0.11484 GlobalStacking 0.116185 optimizer_fallback_total 0
COMPLETED seed 2028 pool expanded4 CTW_SoftOpt 0.110688 GlobalStacking 0.113431 optimizer_fallback_total 0
COMPLETED seed 2028 pool full6 CTW_SoftOpt 0.101727 GlobalStacking 0.113544 optimizer_fallback_total 0
BATCH FINISHED 9 matched seed-pool experiments; method summaries 81
OUTPUT D:\Research\STdeconv_benchmark\results\CTWRF_matched_fusion_20261122_v1
```

## 可直接确认的结论与边界

1. 正式9/9 seed×pool配置成功；输出方法级结果81行（用户脚本运行日志）；所有9个配置optimizer_fallback=0。
2. 9/9种配置CTW_SoftOpt均比GlobalStacking的平均spot JSD数值更低。两方法池：CTW JSD .114838–.114873，Global .116167–.116185；四方法池：CTW .110651–.110690，Global .113383–.113431；六方法池：CTW .101690–.101752，Global .113507–.113544。数据来自同一2000伪spot的不同seed划分，**不代表9个生物独立样本**。
3. seed2026/full6下CTW JSD=0.101752，与历史Proposed_CV约0.1017517246吻合，是算法数值一致性线索，**不能作为新独立外部验证**。
4. 同折是指两种融合策略在每个seed/pool使用相同的五折test indices；模型选择/来源参考等论文最终核查按用户决定交Claude集中审计，现阶段优先补实验。
5. **不能根据JSD推断RMSE整体改善**，下一步需要读取`summary_metrics_by_seed_pool.csv`与`paired_differences_by_seed_pool.csv`和`fit_runtime_by_fold.csv`。
6. 至少历史Global Stacking 36配置已完成、CARR12任务已完成；不要重跑这些已有结果。

## 下一步单个只读PowerShell动作

用户Windows用Python一条`-c`命令读取上述三CSV：
- `summary_metrics_by_seed_pool.csv`：CTW_SoftOpt与GlobalStacking按pool的3seed均值，JSD/matrix_RMSE/aggregated_celltype_RMSE。
- `paired_differences_by_seed_pool.csv`：按against comparator统计9个配置中delta JSD/RMSE方向（`CTW - comparator`，小于0代表CTW更优）。
- `fit_runtime_by_fold.csv`：CTW SoftOpt与GlobalStacking模型fit_seconds的描述性汇总，区分单纯模型拟合与总运行时长。

然后再按原计划安排近期EnDecon最近邻集成文献原文/软件接口对照、真实数据扩展和CARR跨数据集验证。未经用户日志不宣告这些实验已运行。
