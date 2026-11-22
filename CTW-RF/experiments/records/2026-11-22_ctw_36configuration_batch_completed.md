# 2026-11-22 CTW-RF 全局Stacking敏感性：36配置批量实验完成

## 来源与证据等级

[USER_WINDOWS_STDOUT / RUN_LOG_CONFIRMED] 用户本机运行 `CTW-RF/experiments/ctw_stacking_sensitivity_batch.py --run` 后复制末尾控制台输出（目前只看到最后10个COMPLETED行和汇总，没有直接读取完整CSV）：

```text
COMPLETED 2028 strong2 500 JSD 0.115783 matrix_RMSE 0.052696
COMPLETED 2028 strong2 all JSD 0.116185 matrix_RMSE 0.052697
COMPLETED 2028 expanded4 100 JSD 0.111615 matrix_RMSE 0.049784
COMPLETED 2028 expanded4 200 JSD 0.112471 matrix_RMSE 0.049712
COMPLETED 2028 expanded4 500 JSD 0.112921 matrix_RMSE 0.049617
COMPLETED 2028 expanded4 all JSD 0.113431 matrix_RMSE 0.049598
COMPLETED 2028 full6 100 JSD 0.112248 matrix_RMSE 0.049184
COMPLETED 2028 full6 200 JSD 0.112653 matrix_RMSE 0.049098
COMPLETED 2028 full6 500 JSD 0.113016 matrix_RMSE 0.049
COMPLETED 2028 full6 all JSD 0.113544 matrix_RMSE 0.048973
BATCH FINISHED 36 of 36 configurations; FAILED 0
OUTPUT D:\Research\STdeconv_benchmark\results\CTWRF_stacking_sensitivity_20261122_v1
```

之前用户已反馈dry-run:
```text
INPUT CHECK PASS 2000 spots 19 cell types 6 methods
DESIGN 3 seeds x 3 method pools x 4 budgets = 36 configurations
POOL strong2 CARD,cell2location
POOL expanded4 CARD,cell2location,RCTD,SPOTlight
POOL full6 Tangram,RCTD,CellDART,CARD,cell2location,SPOTlight
DRY RUN PASS — no files written
```

## 解释范围

- 批处理程序确认36/36配置计算完成、失败0；2026、2027、2028是预定义随机划分种子，**并非年份/独立生物样本**。
- 本批是对照方法**GlobalStacking**的随机划分、候选池、校准spots预算敏感性，不是CTW-RF Proposed_CV重新训练，不应将其称作最终论文主方法验证完毕。
- 2028 seed末尾full6+all: JSD=0.113544, matrix_RMSE=0.048973；需要按所有36配置查看均值/范围/方向变化。部分强2池JSD较大，但不能从局部输出得出全局稳定性结论。
- 按原计划，未来还需直接CTW-RF vs最近邻集成对照（如经过原文/代码核实的EnDecon）、CTW自身固定折多种split下复算、DLPFC及其它数据，若要进入投稿阶段需审查原始来源/参考独立性；用户要求当前集中推进实验、最终审计交给Claude。

## 原始输出目录

`D:\Research\STdeconv_benchmark\results\CTWRF_stacking_sensitivity_20261122_v1\`

预计：
- `metrics_by_seed_pool_budget.csv` (36×2=72 方法配置行)
- `metrics_by_fold.csv` (36×5×2=360 折指标行)
- `weights_by_fold.csv`
- `descriptive_means_across_seeds.csv` (3×4×2=24 均值行)
- `run_config.json`

数字为脚本设计期望，尚未从用户原始CSV复核。

## 同日两个批处理里程碑

- CARR-lite V2 12任务全部完成：`D:\Research\STdeconv_benchmark\results\CARRliteV2_pending_batch_20261122_v1\batch_metric_means.csv`, `batch_run_status.csv`; 仍待读取实际指标。
- CTW本批36/36完成，失败0。
- **下一步一个只读PowerShell命令统一摘要两个批次**（从各自原始CSV读取，不写文件），随后再安排剩余原计划对照实验。不要重新启动这48个任务或覆盖历史结果。
