# 2026-11-23 CARR-lite V2: 参考细胞构造训练伪spot → 5个留出seqFISH+ FOV，首批实际结果

## 证据级别

[USER_WINDOWS_STDOUT / RUN_LOG_CONFIRMED] 用户运行`carr_reference_only_seqfishplus_batch.py --run --resume --tangram-python D:\ProgramData\miniconda3\envs\Tangram\python.exe`后，提供Windows终端后半段日志。此前检查专业Tangram环境`Tangram import PASS`、`CUDA: False`；已做`--dry-run --resume`通过。此处记录的汇总为**用户运行真实结果**，不是助手在本机替代执行。原始CSV仍在Windows本地，未由助手读取字节。

## 用户贴出的终端结果

```text
TANGRAM train seconds 31.5
  TANGRAM test seconds 8.2
COMPLETED FOV 2 Tangram JSD 0.435083 CARR JSD 0.426708 Tangram singleton AUPRC 0.268805 CARR singleton AUPRC 0.277445
START FOV 3
  TANGRAM train seconds 31.66
  TANGRAM test seconds 7.44
COMPLETED FOV 3 Tangram JSD 0.416578 CARR JSD 0.40647 Tangram singleton AUPRC 0.237374 CARR singleton AUPRC 0.29105
START FOV 4
  TANGRAM train seconds 27.44
  TANGRAM test seconds 5.97
COMPLETED FOV 4 Tangram JSD 0.402643 CARR JSD 0.395503 Tangram singleton AUPRC 0.223233 CARR singleton AUPRC 0.263772
BATCH FINISHED 5 FOV; 15 held-out method/FOV metric rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARR_reference_only_seqfishplus_20261123_v1
                           method  matrix_RMSE  mean_spot_JSD  singleton_RMSE  singleton_vs_zero_AUPRC  singleton_vs_zero_AUROC  zero_prediction_mean
CARR_reference_only_AbundanceOnly     0.097947       0.422088        0.131216                 0.259739                 0.667002              0.035054
     CARR_reference_only_Gate_a50     0.097243       0.423617        0.132314                 0.261662                 0.668072              0.035628
        Tangram_reference_matched     0.099243       0.431365        0.131094                 0.227871                 0.644309              0.035435
```

用户提供的FOV2/3/4描述性差值（CARR Gate a50 − Tangram，注意两者仅为显示6位小数近似）：
- FOV2：JSD −0.008375，singleton AUPRC +0.008640；
- FOV3：JSD −0.010108，singleton AUPRC +0.053676；
- FOV4：JSD −0.007140，singleton AUPRC +0.040539。
FOV0/1的详细指标尚未从用户原始CSV读出，但调度器最终显示5FOV、15行全部完成。绝不猜测FOV0/1逐折值或改善方向。

## 等权FOV均值比较：描述性

| metric | Tangram_reference_matched | CARR_reference_only_Gate_a50 | CARR_reference_only_AbundanceOnly |
|---|---:|---:|---:|
| matrix_RMSE (lower) | 0.099243 | **0.097243** | 0.097947 |
| mean_spot_JSD (lower) | 0.431365 | 0.423617 | **0.422088** |
| singleton_RMSE (lower) | **0.131094** | 0.132314 | 0.131216 |
| singleton_vs_zero_AUPRC (higher) | 0.227871 | **0.261662** | 0.259739 |
| singleton_vs_zero_AUROC (higher) | 0.644309 | **0.668072** | 0.667002 |
| zero_prediction_mean (lower) | 0.035435 | 0.035628 | **0.035054** |

- Gate a50对Tangram：matrixRMSE下降0.002000（约2.02%）、JSD下降0.007748（约1.80%）、singleton AUPRC增加0.033791（约14.83%相对）、AUROC +0.023763；**singleton RMSE升0.001220（约0.93%变差）**，zero_prediction_mean升0.000193（更高）。
- AbundanceOnly相比Gate a50，JSD更低、singleton RMSE更低、zero_prediction_mean更低；Gate a50对AUPRC/AUROC和matrixRMSE稍好。不得宣称门控在所有指标上贡献正收益。
- 这是5个相关FOV的等权描述性均值，pseudo spot由原空间单细胞网格汇聚，**不是5个独立生物重复，也不是70个独立真实测量spot**；未做显著性检验。

## 协议与重要比较限制

- 按已提交方案：每外层FOV从参考细胞按type拆分generator/map，约400个6–12细胞训练合成spot，Tangram训练、测试端使用同一个map参考池，均重新运行，训练CARR固定HGBC三分支12特征、marker40、confusion3、Gate a50。
- 新批**不使用其他目标FOV已知组成真值训练校准器**，测试FOV组成真值只作预测后评价。参考细胞来自同一seqFISH+来源，不能声称从独立测序平台scRNA-seq进行跨平台泛化。
- 与先前使用其它真实FOV训练的历史Gate a50（5FOV mean JSD 0.377208，Singleton AUPRC 0.334900）**并非唯一变量差异**，由于参考拆分和新训练/测试Tangram重拟合，其绝对性能差异不能直接归因于训练数据机制。
- 最终论文审计按用户安排交Claude集中复核；当前不隐瞒局部反例。
- 结果文件：`D:\Research\STdeconv_benchmark\results\CARR_reference_only_seqfishplus_20261123_v1\all_fov_metrics.csv`、`five_fov_descriptive_means.csv`、`paired_fov_differences.csv`，以及各fold训练/预测/日志，默认独立目录、不得覆盖。

## 下一步唯一Windows命令

用Python单条只读命令读取`all_fov_metrics.csv`和`paired_fov_differences.csv`，逐FOV展示Tangram、Gate a50、AbundanceOnly JSD/RMSE/Singleton RMSE/AUPRC以及两CARR相对Tangram的变化计数。借此核实FOV0/1是否出现负结果与指标敏感性，并保存全部五折结果用于后续论文图。之后继续原计划外部平台/CTW外部泛化，不回到旧模拟数据反复扫描参数。
