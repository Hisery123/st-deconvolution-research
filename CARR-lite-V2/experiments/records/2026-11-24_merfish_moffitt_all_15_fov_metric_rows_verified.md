# 2026-11-24 CARR-lite V2 Moffitt MERFISH: 完整5个真实空间切片×3方法=15行原始结果

## 来源与研究状态

[USER_WINDOWS_CSV_READOUT] 用户在Windows读取
`D:\Research\STdeconv_benchmark\results\CARR_MERFISH_Moffitt_sections_20261124_v1\all_fov_metrics.csv`，提供了完整15行`held_out_fov,method,mean_spot_JSD,singleton_vs_zero_AUPRC,singleton_RMSE,matrix_RMSE`原始数值。本次完整实验早已`BATCH FINISHED 5 FOV; 15 held-out method/FOV metric rows`；本记录是**已完成实验的结果归档，不是新增实验或重训**。

## 完整15行用户原始指标（不修改精度）

```csv
held_out_fov,method,mean_spot_JSD,singleton_vs_zero_AUPRC,singleton_RMSE,matrix_RMSE
0,Tangram_reference_matched,0.30239626546938964,0.37934482032986144,0.09278857447328329,0.13445259649789085
0,CARR_reference_only_AbundanceOnly,0.29499225384204464,0.41876735413808563,0.0877736199189305,0.1318475055459988
0,CARR_reference_only_Gate_a50,0.29804271907843033,0.4171620798019474,0.08497475205650631,0.13195374082764103
1,Tangram_reference_matched,0.32253721535666174,0.38691670547488455,0.1035596716764992,0.14623221347324725
1,CARR_reference_only_AbundanceOnly,0.29965531373214643,0.42741909210524787,0.09272947865994784,0.13922236368296811
1,CARR_reference_only_Gate_a50,0.30703518722013773,0.4249143913268386,0.08957215496141864,0.1406387316113792
2,Tangram_reference_matched,0.30781193831161,0.4126739848074018,0.0999804605499257,0.1404903577232104
2,CARR_reference_only_AbundanceOnly,0.26917029683316224,0.5193263336585847,0.08769596974751755,0.1292016046534626
2,CARR_reference_only_Gate_a50,0.2761056637418436,0.5139882544576373,0.08635969850271234,0.13089250156893917
3,Tangram_reference_matched,0.2981387422661426,0.35745134137833845,0.1106125514535189,0.13391085600001593
3,CARR_reference_only_AbundanceOnly,0.28292224232739654,0.42413212129844047,0.10503306641775002,0.12974101160722112
3,CARR_reference_only_Gate_a50,0.28578079598001616,0.41559572033231107,0.10235364074850656,0.13046851237480903
4,Tangram_reference_matched,0.2964085614631447,0.38622561201484507,0.10380238159356883,0.13443129283061203
4,CARR_reference_only_AbundanceOnly,0.29395392338827614,0.38959005640274846,0.09779642079546594,0.13337968288837473
4,CARR_reference_only_Gate_a50,0.2947696759515545,0.39988575706061114,0.0953493611702682,0.13333308399993318
```

## 每折检验与主要比较（脚本外依据上述原值重新计算）

五个FOV每一折`CARR AbundanceOnly`及`Gate_a50`相对`Tangram_reference_matched`均同时满足：
1. `mean_spot_JSD`更低；
2. `matrix_RMSE`更低；
3. `singleton_RMSE`更低；
4. `singleton_vs_zero_AUPRC`更高。

| FOV | AbundanceOnly 相对Tangram JSD降低 | Gate_a50 相对Tangram JSD降低 | AbundanceOnly AUPRC绝对提高 | Gate_a50 AUPRC绝对提高 |
|---|---:|---:|---:|---:|
| 0 | 2.45% | 1.44% | +0.0394 | +0.0378 |
| 1 | 7.09% | 4.81% | +0.0405 | +0.0380 |
| 2 | 12.55% | 10.30% | +0.1067 | +0.1013 |
| 3 | 5.10% | 4.15% | +0.0667 | +0.0581 |
| 4 | 0.83% | 0.55% | +0.0034 | +0.0137 |

**关键负面/权衡：** 五张FOV中`Gate_a50`的`singleton_RMSE`均低于`AbundanceOnly`，但是五张FOV的`mean_spot_JSD`均高于`AbundanceOnly`。门控分支不是全指标改进。AUPRC上Gate只FOV4优于AbundanceOnly，其余FOV0–3劣于AbundanceOnly。更强方法需要定义事先目标指标，不能在看完测试后选择最好分支冒充预注册模型。

## 五折描述性均值（使用给出的逐折数值计算，与用户终端前次6位小数输出一致）

| metric | Tangram | AbundanceOnly | Gate_a50 |
|---|---:|---:|---:|
| mean_spot_JSD ↓ | 0.305458545 | **0.288138806** | 0.292346808 |
| matrix_RMSE ↓ | 0.137903463 | **0.132678434** | 0.133457314 |
| singleton_RMSE ↓ | 0.102148728 | 0.094205711 | **0.091721921** |
| singleton_vs_zero_AUPRC ↑ | 0.384522493 | **0.435846992** | 0.434309241 |

- 相对Tangram，AbundanceOnly JSD均值降低5.67%，Gate降低4.29%；AUPRC相对提升13.35%和12.95%（Abundance AUPRC绝对提高0.051325，Gate提高0.049787）。
- 这些是五个**同一只动物切片**的平均，不能将1750个source-derived bins或5fold视为独立动物。此表不提供跨动物显著性/p值。必须在图表和文中写明n=1 animal、5 preselected sections，每切片350个spatial-bin、测试label是来源注释的conditional ground truth。
- MERFISH `X`为预处理`float32`、大量非整数、无raw层。每个bin由原位细胞真实坐标形成，表达由非Ambiguous标注细胞的预处理信号加和，真值由同一批已标注细胞构造；这是annotation-derived reconstruction，不是原生低分辨率测序的真实spot count比例。
- 每折参考池来自其它11个section，再切generator/mapping，见[外部运行记录](2026-11-24_merfish_moffitt_five_section_external_carr_run_completed.md)；真实单细胞在来源切片间不交叉，但同一动物/跨折train集合高度重叠。最初FOV0运行因KeyboardInterrupt中止、后按相同设置resume完成，全部保留。

## 后续

本批15/15测评结果固定，**不再根据现有测试表现修改CARR、稀有类别门槛、FOV选择或重训**。主要实验已足以启动CARR/CTW两篇论文的Methods/Results结果表与矢量绘图；最终投稿前再做集中统计审查、真值定义核对和最接近相关工作创新性审查。此处严守用户“先完成实验，最后统一审核”，不是另起一次冗长审计。
