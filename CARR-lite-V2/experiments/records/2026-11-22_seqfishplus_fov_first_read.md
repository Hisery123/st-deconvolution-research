# 2026-11-22 seqFISH+ 五个 FOV：首轮只读文件结构与部分指标（用户终端）

## 证据等级

- [USER_WINDOWS_STDOUT] 用户在其 Windows `ST_Clustering` 环境只读以下三个现存本地 CSV，并提供行列数、列名、前8行：
  - `D:\Research\STdeconv_benchmark\data\groundtruth\seqfishplus_cortex_real_spatial_noleak\fold_manifest.csv`，5×8
  - `...\batch_runs\CARR_lite_V2_HGBC_a50\CARR_lite_V2_seqfishplus_metrics_by_fold.csv`，15×12
  - `...\batch_runs\CARR_lite_V2_HGBC_a50\nested_reference_leakage_audit.csv`，20×10
- **注意**：用户只显示了后两个 CSV 的前8行；尚未看到全部15行性能指标、全部20行嵌套隔离审计；绝不能当完整审计完成。
- 目录带有 `real_spatial_noleak`，但同目录还存在 `pseudo_spot_expression.csv`、`pseudo_spot_ground_truth.csv`、`spot_cell_membership.csv`。仅凭目录名不能认定是独立测量的真实spot或模型全过程无泄漏。

## 五折 manifest 原样记录

```csv
held_out_fov,n_target_spots,n_target_cells_retained,n_reference_cells,n_target_cell_types,n_reference_cell_types,n_overlap_cells,unsupported_target_types
0,15,117,795,11,26,0,
1,13,106,805,12,26,0,
2,15,90,823,18,26,0,
3,14,103,807,16,26,0,
4,13,98,812,15,26,0,
```

- 70个spot，保留目标细胞总数514（117+106+90+103+98）；五折 `n_overlap_cells=0` 是该manifest的报告字段，未独立复核每条cell ID和真实原始文件。
- 5个FOV不是5个独立生物学供体；同一FOV内spot相关，不当作70独立重复。

## 用户输出中的前8行 metrics（摘取关键列）

```csv
held_out_fov,method,n_spots,matrix_RMSE,mean_spot_JSD,singleton_n,singleton_RMSE,singleton_vs_zero_AUPRC
0,Tangram,15,0.107503,0.445018,37,0.126703,0.195450
0,V2_AbundanceOnly,15,0.110159,0.436637,37,0.131129,0.216398
0,V2_HGBC_Gate_a50,15,0.106242,0.415259,37,0.121661,0.240731
1,Tangram,13,0.100914,0.449028,39,0.134804,0.233367
1,V2_AbundanceOnly,13,0.099537,0.413685,39,0.142434,0.310875
1,V2_HGBC_Gate_a50,13,0.095436,0.393096,39,0.133093,0.331715
2,Tangram,15,0.095733,0.430034,51,0.148069,0.293444
2,V2_AbundanceOnly,15,0.102932,0.444076,51,0.163592,0.221703
```

- 仅可断言 **FOV2 的V2_AbundanceOnly** 相对Tangram的JSD、singleton RMSE、singleton AUPRC三项均变差；FOV2 `V2_HGBC_Gate_a50` 第9行未在终端可见，**不得把AbundanceOnly的失败误写为三分支版本失败**。
- FOV0/FOV1已展示HGBC_a50指标，JSD与singleton AUPRC相比原版有描述性改善；未完整看到其余三折与统计。

## Nested reference audit（用户可见前8行）

- 全文件 shape 20×10，5外层held-out FOV×4训练FOV。
- 外层FOV0、训练FOV1为 `skipped_missing_nested_reference_types`、缺 `L3`；外层FOV1、训练FOV0同样被跳过（缺 `L3`）。
- 可见使用行 `outer_target_cells_in_nested_reference=0`、`training_target_cells_in_nested_reference=0`，但仍需查看全20行、脚本与原始细胞ID来源以核实其他环节。
- 跳过训练FOV可能影响不同外层折有效训练样本数；不应默认每折都有4个训练FOV参与拟合。

## 下一步：唯一只读命令（尚未执行）

输出完整15行核心性能和20行嵌套审计状态（不修改任何文件）：

```powershell
python -c "import pandas as pd; from pathlib import Path; r=Path(r'D:\Research\STdeconv_benchmark\data\groundtruth\seqfishplus_cortex_real_spatial_noleak\batch_runs\CARR_lite_V2_HGBC_a50'); m=pd.read_csv(r/'CARR_lite_V2_seqfishplus_metrics_by_fold.csv'); a=pd.read_csv(r/'nested_reference_leakage_audit.csv'); print('FOLD METRICS, rows',len(m)); print(m[['held_out_fov','method','n_spots','mean_spot_JSD','singleton_RMSE','singleton_vs_zero_AUPRC','singleton_vs_zero_AUROC']].to_string(index=False)); print('NESTED AUDIT, rows',len(a)); print(a[['held_out_fov','training_fov','status','missing_cell_types','outer_target_cells_in_nested_reference','training_target_cells_in_nested_reference']].to_string(index=False)); print('STATUS COUNTS'); print(a.groupby(['held_out_fov','status']).size().to_string())"
```

- 若文件读取、列名错误，需用户发送原始报错；不要修改已完成实验结果。
