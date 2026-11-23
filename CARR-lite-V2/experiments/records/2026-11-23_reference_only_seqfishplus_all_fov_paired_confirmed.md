# 2026-11-23 CARR reference-cell-only训练→留出seqFISH+ 5 FOV：全部15行性能与10行配对差值

## 证据等级和来源

[USER_WINDOWS_CSV_SUMMARY] 用户在Windows本机，用Python/pandas只读以下已完成批处理生成的文件，完整打印逐FOV指标和配对差值。本文逐项转录用户终端真实输出，不代表助手已直接取得本地原始CSV字节。

- `D:\Research\STdeconv_benchmark\results\CARR_reference_only_seqfishplus_20261123_v1\all_fov_metrics.csv`
- 同目录`paired_fov_differences.csv`
- 前序`five_fov_descriptive_means.csv`在用户终端打印的等FOV均值，参考[批处理成功摘要](2026-11-23_reference_only_seqfishplus_batch_complete.md)。

**真实实验状态**：5个FOV×3方法=15方法/FOV行，CARR三分支和matched-reference Tangram均由用户Windows批处理产生，非助手本地运行。此处没有独立供体统计检验，也不把70spots/400训练合成spot当独立生物样本。

## 15行逐FOV完整主要指标（原用户终端，保留6位小数）

```csv
held_out_fov,method,matrix_RMSE,mean_spot_JSD,singleton_RMSE,singleton_vs_zero_AUPRC
0,CARR_reference_only_AbundanceOnly,0.106519,0.441680,0.127220,0.213158
0,CARR_reference_only_Gate_a50,0.106480,0.447856,0.130288,0.210449
0,Tangram_reference_matched,0.107448,0.447747,0.127135,0.180198
1,CARR_reference_only_AbundanceOnly,0.100916,0.447775,0.137395,0.258836
1,CARR_reference_only_Gate_a50,0.099071,0.441549,0.136361,0.265596
1,Tangram_reference_matched,0.101763,0.454775,0.136972,0.229748
2,CARR_reference_only_AbundanceOnly,0.095282,0.423033,0.150642,0.279775
2,CARR_reference_only_Gate_a50,0.094737,0.426708,0.151987,0.277445
2,Tangram_reference_matched,0.096460,0.435083,0.151093,0.268805
3,CARR_reference_only_AbundanceOnly,0.089496,0.403064,0.119271,0.302988
3,CARR_reference_only_Gate_a50,0.089088,0.406470,0.119589,0.291050
3,Tangram_reference_matched,0.091802,0.416578,0.121137,0.237374
4,CARR_reference_only_AbundanceOnly,0.097520,0.394887,0.121553,0.243938
4,CARR_reference_only_Gate_a50,0.096840,0.395503,0.123346,0.263772
4,Tangram_reference_matched,0.098744,0.402643,0.119135,0.223233
```

## 10行配对改善（CARR−matched Tangram；来自实际未四舍五入原CSV计算、这里6位显示）

```csv
held_out_fov,method,delta_mean_spot_JSD,delta_matrix_RMSE,delta_singleton_RMSE,delta_singleton_vs_zero_AUPRC
0,CARR_reference_only_AbundanceOnly,-0.006067,-0.000929,+0.000084,+0.032960
0,CARR_reference_only_Gate_a50,+0.000109,-0.000968,+0.003153,+0.030251
1,CARR_reference_only_AbundanceOnly,-0.007001,-0.000846,+0.000423,+0.029088
1,CARR_reference_only_Gate_a50,-0.013227,-0.002691,-0.000611,+0.035848
2,CARR_reference_only_AbundanceOnly,-0.012049,-0.001178,-0.000451,+0.010970
2,CARR_reference_only_Gate_a50,-0.008375,-0.001723,+0.000895,+0.008640
3,CARR_reference_only_AbundanceOnly,-0.013514,-0.002306,-0.001866,+0.065615
3,CARR_reference_only_Gate_a50,-0.010108,-0.002714,-0.001548,+0.053676
4,CARR_reference_only_AbundanceOnly,-0.007756,-0.001224,+0.002418,+0.020705
4,CARR_reference_only_Gate_a50,-0.007140,-0.001903,+0.004211,+0.040539
```

## 严谨结论

1. **Gate a50**对matched Tangram：singleton-vs-zero AUPRC 5/5个FOV改善、matrixRMSE 5/5改善、mean spot JSD 4/5改善（FOV0 +0.000109轻微变差）、singletonRMSE 2/5改善（FOV0/2/4变差）。各FOV AUPRC改善量 +0.030251 / +0.035848 / +0.008640 / +0.053676 / +0.040539。
2. **AbundanceOnly**对matched Tangram：mean spot JSD 5/5改善、matrixRMSE 5/5改善、AUPRC 5/5改善、singletonRMSE 2/5改善。Gate a50的JSD在FOV0/2/3/4劣于AbundanceOnly，只有FOV1优于AbundanceOnly。Gate a50的singletonAUPRC在FOV0/2/3劣于AbundanceOnly，FOV1/4优于AbundanceOnly。
3. 前序用户打印五FOV等权均值：matched Tangram JSD .431365、matrixRMSE .099243、singletonRMSE .131094、singleton AUPRC .227871；CARR Gate a50 .423617/.097243/.132314/.261662；AbundanceOnly .422088/.097947/.131216/.259739；**门控不具备所有指标/所有FOV优势，不能把所有收益归因于门控模块。**
4. `singleton_vs_zero_AUPRC`仅比较**singletons vs zero**，不代表所有稀有阳性定义下的AUPRC。Matrix RMSE是整个spot×celltype组成误差，而singleton RMSE限定恰有一个成员细胞类别；两者可出现方向相反。
5. 5个FOV来自同一seqFISH+空间单细胞来源，70个spots为真实空间定位细胞聚合成pseudo spots，非物理独立测量的空间捕获spot；5FOV不自动等于5独立供体。每FOV仅15/13/15/14/13个spot，趋势属于**探索性描述统计**，不能据此直接给独立样本显著性结论。
6. 本批使用参考细胞合成训练伪spot，而非其他FOV目标真值来训练CARR；参考仍来自seqFISH+同域，不是独立平台scRNA；用同一个mapping池分别重跑训练和测试Tangram。不能将本批相较旧五FOV实验的绝对变化单独归因为训练机制，因为基础参考拆分及Tangram也改变了。

## 目前最佳可陈述的论文主张

“在由seqFISH+真实空间单细胞位置聚合的5个留出FOV基准上，单细胞参考数据构造的合成训练伪spot校准器相对于使用匹配参考池的Tangram，在全部5个FOV改善singleton-vs-zero检测AUPRC以及整体matrixRMSE；但singleton丰度定量RMSE只在2/5 FOV改善，说明检测收益尚不能等价于稀有细胞定量能力提升。”这是**探索性同源数据结果**，不是跨平台验证、独立生物重复或新模型的创新性证明。

## 执行下一步

用户希望先推进剩余实验，最终Claude做全面审计；**不再在当前这套seqFISH+ 5FOV数据上重复后验门控或随机种子参数扫描**。接下来应考虑真实独立来源的数据集（须核实原始文件、真实组成真值/独立单位、与当前模型的共享细胞类型和基因覆盖）或CTW在新切片/样本上的外部验证。尚未执行新的外部数据实验，不应报成已完成。
