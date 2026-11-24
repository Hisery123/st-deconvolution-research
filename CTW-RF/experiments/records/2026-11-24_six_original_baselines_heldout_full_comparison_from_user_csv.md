# 2026-11-24 CTW原六方法严格来源细胞隔离：54行CSV中关键24行实测对照、正负结果同报

## 来源与状态

[USER_WINDOWS_CSV_READOUT] 用户Windows执行`Import-Csv D:\Research\STdeconv_benchmark\results\CTWRF_six_method_disjoint_20261123_v1\heldout_metrics_by_scenario_pool.csv`，终端明确`TOTAL METRIC ROWS: 54`。用户按6组挑出了`CTW_SoftOpt`、`GlobalStacking`、`EqualWeight`以及**该组测试JSD最低的单一基线**，合计24行；以下均来自本次用户实际CSV控制台显示，不是助手本地下载全部54行而直接重算。六方法24个正式基础任务、6组对照已经完成，详见[前一真实运行记录](2026-11-24_six_original_baselines_cell_disjoint_batch_completed.md)。

## 关键 JSD 对比（↓越低越好）

| sampling | pool | CTW SoftOpt JSD | Global Stacking JSD | EqualWeight JSD | 同池测试JSD最低单方法 | 单方法JSD | CTW比Global改善 |
|---|---|---:|---:|---:|---|---:|---:|
| balanced_celltype | strong2 | 0.225140187 | 0.229201990 | 0.225236913 | CARD | 0.229757509 | 1.772% |
| balanced_celltype | expanded4 | 0.210974484 | 0.221771494 | 0.219598908 | CARD | 0.229757509 | 4.869% |
| balanced_celltype | full6 | 0.213509624 | 0.224154395 | 0.236801128 | CARD | 0.229757509 | 4.749% |
| cell_uniform | strong2 | 0.178680319 | 0.182653462 | **0.177836177** | cell2location | 0.180170522 | 2.175% |
| cell_uniform | expanded4 | 0.150112962 | 0.156552068 | 0.174227525 | RCTD | 0.162299414 | 4.113% |
| cell_uniform | full6 | **0.139747598** | 0.145139861 | 0.163675978 | Tangram | 0.144008665 | 3.715% |

改善率精确定义`(GlobalJS D - CTWJS D)/GlobalJS D *100%`；仅按用户文本计算，保留3位小数。不存在该表之外的推断统计显著性。

## Matrix RMSE与aggregated-celltype RMSE真实对照

| sampling | pool | CTW matrixRMSE | Global matrixRMSE | CTW agg-celltypeRMSE | Global agg-celltypeRMSE |
|---|---|---:|---:|---:|---:|
| balanced_celltype | strong2 | 0.077258486 | **0.076796982** | 1.289683194 | **1.286573858** |
| balanced_celltype | expanded4 | **0.071812127** | 0.071983269 | **1.154238449** | 1.169912735 |
| balanced_celltype | full6 | 0.072947085 | **0.072312228** | **1.174659848** | 1.176678675 |
| cell_uniform | strong2 | **0.077520328** | 0.077901935 | 1.157484748 | **1.155381758** |
| cell_uniform | expanded4 | **0.064737774** | 0.068723615 | **0.969184085** | 1.026197356 |
| cell_uniform | full6 | **0.062084694** | 0.064279168 | **0.933908767** | 0.975614189 |

比较说明：以JSD为衡量，CTW SoftOpt在此测试集的**六组均低于GlobalStacking（6/6）**；**六组均低于同池“测试后筛选最低JSD”的单一方法（6/6）**；但与EqualWeight为**5/6**，`cell_uniform/strong2` EqualWeight 0.177836177 < CTW 0.178680319（相对劣0.475%）。以matrix RMSE看，CTW对Global仅**4/6**较低：`balanced/strong2`及`balanced/full6`为负结果；以aggregated-celltype RMSE看，CTW对Global亦**4/6**较低，例外为`balanced/strong2`与`cell_uniform/strong2`。这些不能在论文中隐藏。

## 完整用户终端选出24行（列值精度按原文）

```csv
scenario,pool,method,JSD,matrix_RMSE,aggregated_celltype_RMSE
balanced_celltype,strong2,EqualWeight,0.22523691316784344,0.07874725180044366,1.3111974677182523
balanced_celltype,strong2,GlobalStacking,0.22920199016205775,0.07679698215283105,1.286573857851876
balanced_celltype,strong2,CTW_SoftOpt,0.22514018735473917,0.0772584863017182,1.2896831937497781
balanced_celltype,strong2,CARD,0.2297575085743611,0.07677518795097228,1.286719375238512
balanced_celltype,expanded4,EqualWeight,0.2195989080110702,0.0730395481552467,1.1944349926758493
balanced_celltype,expanded4,GlobalStacking,0.22177149405601732,0.07198326904212604,1.1699127347172755
balanced_celltype,expanded4,CTW_SoftOpt,0.2109744844940129,0.07181212663966906,1.1542384487261392
balanced_celltype,expanded4,CARD,0.2297575085743611,0.07677518795097228,1.286719375238512
balanced_celltype,full6,EqualWeight,0.2368011284070822,0.07806247573064355,1.2663538588207512
balanced_celltype,full6,GlobalStacking,0.22415439537652015,0.07231222785974885,1.1766786753148486
balanced_celltype,full6,CTW_SoftOpt,0.21350962399266799,0.0729470846044562,1.1746598479127852
balanced_celltype,full6,CARD,0.2297575085743611,0.07677518795097228,1.286719375238512
cell_uniform,strong2,EqualWeight,0.17783617703769813,0.07900319417776826,1.1747881280201034
cell_uniform,strong2,GlobalStacking,0.18265346199455085,0.07790193468973344,1.155381758006493
cell_uniform,strong2,CTW_SoftOpt,0.17868031858606634,0.07752032756818045,1.157484748145577
cell_uniform,strong2,cell2location,0.18017052208632342,0.08267688784917279,1.2284630023945424
cell_uniform,expanded4,EqualWeight,0.17422752505461567,0.07162807388709327,1.0504908840846567
cell_uniform,expanded4,GlobalStacking,0.1565520681137485,0.06872361453189967,1.0261973563855802
cell_uniform,expanded4,CTW_SoftOpt,0.1501129618127683,0.06473777399221084,0.9691840846294502
cell_uniform,expanded4,RCTD,0.16229941357875013,0.07231981260737479,1.0859557260761505
cell_uniform,full6,EqualWeight,0.16367597838899933,0.06905241669827245,1.022276040411737
cell_uniform,full6,GlobalStacking,0.14513986119490135,0.06427916814616559,0.9756141885382439
cell_uniform,full6,CTW_SoftOpt,0.13974759764953212,0.062084693556324066,0.9339087666566407
cell_uniform,full6,Tangram,0.14400866475546262,0.06295822359360694,0.9693678021914847
```

## 重要科学解释边界

- 最佳单方法由**测试结果排序**选出，适合作为“同池事后最佳单方法参考线”，**不可冒充事先在train集选择的可部署模型**；要进行预测部署意义对照应另设train-only选择器及test评价，当前暂不针对已完成测试做后验调参。
- 两种sampling共享同一个cortex-SVZ原始cell来源的不同随机同组重抽，三方法池在每情景也共享同一train/test真值与基础预测，**6/6不是6个生物独立重复**；禁止以6为独立供体推断显著性。
- 真实DLPFC12切片无比例真值、应用实验已完成且不参与本轮JSD计算。
- 本结果显示基于来源细胞ID的严格隔离测试的内部一致正面结果，同时RMSE和等权融合存在负结果；不说明跨供体/平台通用优越或新方法创新性已被证实。

## 后续

应按照用户“先完成实验再最后统一审查”承诺：锁定本轮结果，不重跑24方法或根据测试表现改变权重/超参。下一项可转外部独立有空间cell-type真值的第二平台，若尚无数据则先做最少一次只读资料定位，避免把模拟MERFISH当真实空间验证。
