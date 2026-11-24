# 2026-11-24 CTW-RF原六方法严格参考细胞与伪spot来源细胞无交叉：Windows完整运行成功

## 证据等级与状态

[USER_WINDOWS_CONSOLE, COMPLETED] 用户亲自在Windows执行此前已通过dry-run的
`ctw_six_baselines_cell_disjoint_batch.py --run`，终端最终打印：

```text
EVALUATED balanced_celltype strong2 CTW_SoftOpt JSD 0.22514 softopt_fallback 0
EVALUATED balanced_celltype expanded4 CTW_SoftOpt JSD 0.210974 softopt_fallback 0
EVALUATED balanced_celltype full6 CTW_SoftOpt JSD 0.21351 softopt_fallback 0
EVALUATED cell_uniform strong2 CTW_SoftOpt JSD 0.17868 softopt_fallback 0
EVALUATED cell_uniform expanded4 CTW_SoftOpt JSD 0.150113 softopt_fallback 0
EVALUATED cell_uniform full6 CTW_SoftOpt JSD 0.139748 softopt_fallback 0
BATCH FINISHED 2 scenarios, 24/24 base method runs, 6 matched pool evaluations; 54 held-out metric rows
OUTPUT D:\Research\STdeconv_benchmark\results\CTWRF_six_method_disjoint_20261123_v1
```

**截至本归档，终端已确认全部24个原始基础方法任务成功且54行测试指标生成，但助手尚未读取那份54行原始CSV，不能猜测GlobalStacking、EqualWeight、各单方法JSD/RMSE，也不能断言CTW胜过任何尚未读取的比较者。** 原研究同一cortex-SVZ来源的细胞ID隔离，不是独立供体/动物/平台级复现；训练伪spot在同组donor细胞之间仍有重复取样，不能将spot视作独立生物学重复。

## 24/24方法任务真实终端耗时（秒）

| 采样 | 部分 | Tangram | RCTD | CellDART | CARD | cell2location | SPOTlight |
|---|---|---:|---:|---:|---:|---:|---:|
| balanced_celltype | train | 67.1 | 405.7 | 266.1 | 36.6 | 16527.1 | 71.5 |
| balanced_celltype | test | 44.6 | 401.3 | 249.1 | 28.6 | 6413.0 | 64.8 |
| cell_uniform | train | 64.8 | 417.9 | 258.1 | 42.2 | 10287.5 | 89.0 |
| cell_uniform | test | 47.0 | 408.4 | 251.6 | 42.7 | 6212.1 | 60.6 |

全部日志都是每个`START ...`之后出现`DONE ...`，无失败方法。第一批cell2location在Windows曾经显示基因筛选Matplotlib Figure；研究者手动关闭图窗后训练继续完成。

## 六种CTW_SoftOpt JSD：真实终端结果

| 采样 | pool | CTW SoftOpt JSD | SoftOpt fallback |
|---|---|---:|---:|
| balanced_celltype | strong2 | 0.225140 | 0 |
| balanced_celltype | expanded4 | 0.210974 | 0 |
| balanced_celltype | full6 | 0.213510 | 0 |
| cell_uniform | strong2 | 0.178680 | 0 |
| cell_uniform | expanded4 | 0.150113 | 0 |
| cell_uniform | full6 | 0.139748 | 0 |

方法池预先固定：strong2=CARD+cell2location；expanded4=前者+RCTD+SPOTlight；full6=Tangram+RCTD+CellDART+CARD+cell2location+SPOTlight。训练1200伪spot只用train donor单细胞来源，测试800伪spot只用test donor来源，419 reference单细胞无交叉。相同sampling场景的3个方法池共用同一test实例，不能当独立样本；两个sampling场景也使用同一原始source biological样本集合，不能当独立动物重复。

## 结果文件和后续

结果目录：
`D:\Research\STdeconv_benchmark\results\CTWRF_six_method_disjoint_20261123_v1`

关键文件：
- `baseline_task_status.csv`：24个方法任务的状态和耗时；
- `heldout_metrics_by_scenario_pool.csv`：54行测试结果，需用户Windows输出/上传才能比较全部方法；
- `frozen_weights_by_scenario_pool.csv`：训练来源校准后冻结的融合权重；
- `logs/`：逐任务真实日志；
- `views/<scenario>/<train|test>/predictions/`：各方法新预测，不能混入旧同细胞重叠来源的结果；
- `fusion_predictions/`：各方法池的测试预测。

下一步按用户“先完成实验再综合审计”的偏好：**不重跑完成的24任务，不改算法或针对当前测试集调参**。让用户执行单条只读PowerShell命令打印54行表（至少包含scenario,pool,method,JSD,matrix_RMSE），依据真实原始CSV补齐与单方法、EqualWeight和GlobalStacking的量化对照；随后若CARR/CTW外部新数据仍需做才推进其它实验，最终Claude集中进行独立单位统计和论文审计。
