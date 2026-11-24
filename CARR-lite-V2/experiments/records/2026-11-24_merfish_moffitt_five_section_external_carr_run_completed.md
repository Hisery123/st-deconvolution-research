# 2026-11-24 CARR-lite V2 Moffitt MERFISH真实空间跨切片外部验证：正式5/5完成

## 实验状态、证据等级

[USER_WINDOWS_CONSOLE, COMPLETE] 用户在Windows上以`carr_reference_only_seqfishplus_batch.py --run --resume --data-root ...\MERFISH_Moffitt_2018\carr_sections_v1 --out-dir ...\CARR_MERFISH_Moffitt_sections_20261124_v1 --tangram-python ...\envs\Tangram\python.exe --density-prior uniform`完成批次。首次`FOV0 train Tangram`被`KeyboardInterrupt`终止，随后相同配置`--run --resume`恢复，第二次用户已显示`TANGRAM train seconds 12.06`；本次最新终端明确：

```text
TANGRAM test seconds 10.5
COMPLETED FOV 1 Tangram JSD 0.322537 CARR JSD 0.307035 Tangram singleton AUPRC 0.386917 CARR singleton AUPRC 0.424914
START FOV 2
  TANGRAM train seconds 11.11
  TANGRAM test seconds 10.79
COMPLETED FOV 2 Tangram JSD 0.307812 CARR JSD 0.276106 Tangram singleton AUPRC 0.412674 CARR singleton AUPRC 0.513988
START FOV 3
  TANGRAM train seconds 11.23
  TANGRAM test seconds 11.13
COMPLETED FOV 3 Tangram JSD 0.298139 CARR JSD 0.285781 Tangram singleton AUPRC 0.357451 CARR singleton AUPRC 0.415596
START FOV 4
  TANGRAM train seconds 11.83
  TANGRAM test seconds 11.69
COMPLETED FOV 4 Tangram JSD 0.296409 CARR JSD 0.29477 Tangram singleton AUPRC 0.386226 CARR singleton AUPRC 0.399886
BATCH FINISHED 5 FOV; 15 held-out method/FOV metric rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARR_MERFISH_Moffitt_sections_20261124_v1
                           method  matrix_RMSE  mean_spot_JSD  singleton_RMSE  singleton_vs_zero_AUPRC  singleton_vs_zero_AUROC  zero_prediction_mean
CARR_reference_only_AbundanceOnly     0.132678       0.288139        0.094206                 0.435847                 0.749590              0.046960
     CARR_reference_only_Gate_a50     0.133457       0.292347        0.091722                 0.434309                 0.750083              0.047932
        Tangram_reference_matched     0.137903       0.305459        0.102149                 0.384522                 0.724787              0.048470
```

**五折总完成的证据为BATCH FINISHED及15行输出，不需要另行重复运行。** 用户这次只贴FOV1–4的单折数值，FOV0单折数值尚未贴出，不能把截取的四折当成五折各自独立完整证据。完整五折summary是程序实际输出。

## 5个FOV描述性平均指标与对照

| 统计指标 | Tangram reference matched | CARR reference-only AbundanceOnly | CARR reference-only Gate_a50 |
|---|---:|---:|---:|
| matrix_RMSE ↓ | 0.137903 | **0.132678** | 0.133457 |
| mean_spot_JSD ↓ | 0.305459 | **0.288139** | 0.292347 |
| singleton_RMSE ↓ | 0.102149 | 0.094206 | **0.091722** |
| singleton_vs_zero_AUPRC ↑ | 0.384522 | **0.435847** | 0.434309 |
| singleton_vs_zero_AUROC ↑ | 0.724787 | 0.749590 | **0.750083** |
| zero_prediction_mean ↓ | 0.048470 | **0.046960** | 0.047932 |

由用户终端平均值算出、仅描述性：
- **AbundanceOnly** vs Tangram：JSD相对降低**5.670%**；matrix RMSE降低**3.789%**；singleton RMSE降低**7.776%**；singleton AUPRC相对提高**13.348%**（绝对提高0.051325）；singleton AUROC相对提高3.422%。
- **Gate_a50** vs Tangram：JSD相对降低**4.293%**；matrix RMSE降低3.224%；singleton RMSE降低**10.208%**；singleton AUPRC相对提高12.948%（绝对提高0.049787）；singleton AUROC相对提高3.490%。
- **不利于Gate的结果必须记录**：相较AbundanceOnly，Gate_a50整体JSD更差（0.292347 > 0.288139）、matrix RMSE更差（0.133457 > 0.132678）、singleton AUPRC略低（0.434309 < 0.435847），zero_prediction_mean也略高；但Gate_a50有更低singleton RMSE和略高AUROC。这支持两者在不同指标上的权衡，不能宣称Gate全面增益。

## 实验来源、控制与科学边界

- 新的独立**公开研究和测量技术**来源Moffitt 2018 小鼠下丘脑MERFISH（73,655cells、161测量基因），原source`Animal_ID`只有**一个**，12个Bregma sections；预先选了Bregma -29/-14/-4/11/26五张留出sections，每张350个由原位细胞(x,y)坐标固定空间格网构成的bins，**并非五个独立生物学动物，不能直接计算多动物置信区间或p值**。同一研究内部的reference+train与test按section严格不交叉；不是在seqFISH+上训练再跨平台迁移到MERFISH。
- 数据`X`为非负`float32`、大量非整数值（约38.99%采样非整数正值）、无anndata`layers`及`.raw`；不能视为原始RNA molecule count。无RTCD/cell2location的要求raw count对照。Tangram以`density_prior=uniform`，`device=cpu`、500epochs、400 source-reference-generated synthetic training spots/fold；CARR同原验证的12特征、`confusion_k=3, marker_k=40, Gate_a50`。
- 作者Cell_class 16个类别含`Ambiguous`，在实验输入中排除Ambiguous（本源9,282个）；预测共15确信类别；**测试bin真值是作者标签下“可明确注释细胞”中的annotation-derived比例，而非真实Visium spot人工测得的分子级混合真值**；bin表达亦由同一注释筛选后细胞X加和，而非原位原生低分辨率测序spot。目标bin空间几何按全部细胞位置及计数确定，类别标签仅用于生成固定 benchmark 的表达/真值；阈值、bin宽及持出折不依据测试结果改变。
- 5fold同一动物且共享11个training sections，存在样本关联性、不是独立生物重复；五折是空间/技术条件下的描述性验证。没有声称显著性、临床性能或超越所有现有方法。
- 本次映射使用Tangram旧Python3.7`torch1.13.1+cpu`，用户明确**只有未来cell2location需要GPU，其他算法保持CPU旧环境**，不应创建Tangram-GPU改动本批。
- CTW先前六原方法source-cell-disjoint 24/24和DLPFC12slice结果均已完成并冻结，与本批CARR指标不要混成同一实验。

## 下一步（只读汇总后开始写作）

- 不重跑、不根据已见test结果调参/挑切片；通过**单条只读PowerShell**输出`all_fov_metrics.csv`关键每折JSD、singleton AUPRC、matrix RMSE及`paired_fov_differences.csv`，尤其补齐未呈现的FOV0和正负折异质性，确定能否报告每折优于Tangram及在何种指标不优。该阶段是汇总已生成结果，不是新实验，更不是碎片重复审查。
- 然后基于已完成CTW/CARR开始Methods/Results结构、图表绘制、最终Claude综合科研审查和文献创新性核对；新外部验证只证明新来源空间内部留出，不是跨动物生物学外部replication。
