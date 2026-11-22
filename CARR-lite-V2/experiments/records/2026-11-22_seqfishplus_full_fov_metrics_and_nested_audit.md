# 2026-11-22 seqFISH+ 五 FOV：完整15行历史指标与20行嵌套参考审计

## 证据来源与性质

- [USER_WINDOWS_STDOUT] 用户通过 pandas 从本机 `seqfishplus_cortex_real_spatial_noleak/batch_runs/CARR_lite_V2_HGBC_a50` 中只读 `CARR_lite_V2_seqfishplus_metrics_by_fold.csv` 与 `nested_reference_leakage_audit.csv`，提供了所有15条指标和20条审计记录。
- 此次为**历史结果的独立对话转录和初步汇总**，尚未取得源CSV字节、核算脚本和完整细胞ID表。目录名`real_spatial_noleak`不能证实“原始独立测量spot”或“整个流程无泄漏”。
- 五个留出FOV总共70个spot，spot来自何种构造仍待审查。不能把70个spot或5个FOV冒称独立生物学重复。

## 完整五折评价原始控制台数值

```csv
held_out_fov,method,n_spots,mean_spot_JSD,singleton_RMSE,singleton_vs_zero_AUPRC,singleton_vs_zero_AUROC
0,Tangram,15,0.445018,0.126703,0.195450,0.614288
0,V2_AbundanceOnly,15,0.436637,0.131129,0.216398,0.626236
0,V2_HGBC_Gate_a50,15,0.415259,0.121661,0.240731,0.691332
1,Tangram,13,0.449028,0.134804,0.233367,0.616035
1,V2_AbundanceOnly,13,0.413685,0.142434,0.310875,0.636659
1,V2_HGBC_Gate_a50,13,0.393096,0.133093,0.331715,0.676050
2,Tangram,15,0.430034,0.148069,0.293444,0.653900
2,V2_AbundanceOnly,15,0.444076,0.163592,0.221703,0.588480
2,V2_HGBC_Gate_a50,15,0.417433,0.157866,0.247989,0.629039
3,Tangram,14,0.406412,0.118854,0.258527,0.700757
3,V2_AbundanceOnly,14,0.299807,0.127080,0.433419,0.767472
3,V2_HGBC_Gate_a50,14,0.299913,0.113301,0.474637,0.809376
4,Tangram,13,0.401457,0.119911,0.214573,0.726775
4,V2_AbundanceOnly,13,0.375886,0.120549,0.316091,0.743588
4,V2_HGBC_Gate_a50,13,0.360341,0.108989,0.379427,0.793343
```

## 五折 Tangram vs 三分支 Gate_a50 变化（CARR − Tangram）

| held-out FOV | Δmean spot JSD | Δsingleton RMSE | Δsingleton-vs-zero AUPRC | ΔAUROC |
|---|---:|---:|---:|---:|
| 0 | -0.029759 | -0.005042 | +0.045281 | +0.077044 |
| 1 | -0.055932 | -0.001711 | +0.098348 | +0.060015 |
| 2 | -0.012601 | **+0.009797（变差）** | **-0.045455（变差）** | **-0.024861（变差）** |
| 3 | -0.106499 | -0.005553 | +0.216110 | +0.108619 |
| 4 | -0.041116 | -0.010922 | +0.164854 | +0.066568 |

- JSD改善 **5/5 FOV**；singleton RMSE、singleton-vs-zero AUPRC、AUROC各改善 **4/5 FOV**。
- FOV2 是三分支CARR版本的**真实历史负结果**，不能仅用AbundanceOnly失败代替；Gate_a50 FOV2 JSD仍改善，但singleton检测/定量均恶化。
- 由显示到六位小数的五折数据计算出的**五FOV等权描述性均值**：mean spot JSD Tangram `0.426390`、Gate_a50 `0.377208`；singleton-vs-zero AUPRC Tangram `0.239072`、Gate_a50 `0.334900`。这与此前项目稿件的历史报告数字一致，仍非重新读取原始CSV独立复算，也不能据此发明显著性。
- `singleton`的定义必须回看指标评价代码：本文件按源列名`singleton_vs_zero_AUPRC`报告，不能泛化为所有rare-positive AUPRC。

## 20行 Nested Reference 审计：完整状态

| held_out_fov | training_fov | status | missing_cell_types | outer_target_cells_in_nested_reference | training_target_cells_in_nested_reference |
|---:|---:|---|---|---:|---:|
| 0 | 1 | skipped_missing_nested_reference_types | L3 | 0 | 0 |
| 0 | 2 | used | — | 0 | 0 |
| 0 | 3 | used | — | 0 | 0 |
| 0 | 4 | used | — | 0 | 0 |
| 1 | 0 | skipped_missing_nested_reference_types | L3 | 0 | 0 |
| 1 | 2 | used | — | 0 | 0 |
| 1 | 3 | used | — | 0 | 0 |
| 1 | 4 | used | — | 0 | 0 |
| 2 | 0 | used | — | 0 | 0 |
| 2 | 1 | used | — | 0 | 0 |
| 2 | 3 | used | — | 0 | 0 |
| 2 | 4 | used | — | 0 | 0 |
| 3 | 0 | used | — | 0 | 0 |
| 3 | 1 | used | — | 0 | 0 |
| 3 | 2 | used | — | 0 | 0 |
| 3 | 4 | used | — | 0 | 0 |
| 4 | 0 | used | — | 0 | 0 |
| 4 | 1 | used | — | 0 | 0 |
| 4 | 2 | used | — | 0 | 0 |
| 4 | 3 | used | — | 0 | 0 |

- 有效 `used` = **18/20** 内层训练FOV组合，跳过 `2/20`（FOV0的train FOV1、FOV1的train FOV0，缺L3）。FOV0/FOV1每折实际使用3/4个可选训练FOV；FOV2/3/4使用4/4个。
- 用户展示的所有20行的`outer_target_cells_in_nested_reference`、`training_target_cells_in_nested_reference`都报告 0，**但跳过行中的0不能证明曾拟合参考**。使用行的细胞ID重叠报告0，只能支持审计表定义下的嵌套隔离，不能覆盖其它泄漏路径或外部泛化。
- `fold_manifest.csv` 首轮显示5折`n_overlap_cells=0`，合计70目标spot、514保留目标细胞；仍要独立核对 cell-ID和spot membership、源码。

## 下一步唯一人工命令

只读查看构建来源数据的形状、关键列和前两行（不写文件）：

```powershell
python -c "import pandas as pd; from pathlib import Path; r=Path(r'D:\Research\STdeconv_benchmark\data\groundtruth\seqfishplus_cortex_real_spatial_noleak'); fs=['cell_metadata_aligned.csv','spot_cell_membership.csv','pseudo_spot_locations.csv','pseudo_spot_ground_truth.csv']; [(print('\nFILE',f,'SHAPE',x.shape,'COLUMNS',list(x.columns)),print(x.head(2).to_string(index=False))) for f in fs for x in [pd.read_csv(r/f)]]"
```

目的：辨别是否基于真实成像定位的单细胞汇聚成pseudo spots，厘清spot与cell对应关系，以及FOV独立性；若目录名无法验证，不宣传为独立真实spot实验。
