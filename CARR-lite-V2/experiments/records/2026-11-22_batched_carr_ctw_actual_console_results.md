# 2026-11-22 两篇论文批处理结果：用户Windows CSV读取汇总（真实数值）

## 来源与状态

[USER_WINDOWS_STDOUT] 用户亲自使用 pandas 读取本机：
- `D:\Research\STdeconv_benchmark\results\CARRliteV2_pending_batch_20261122_v1\batch_run_status.csv`
- 同目录 `batch_metric_means.csv`
- `D:\Research\STdeconv_benchmark\results\CTWRF_stacking_sensitivity_20261122_v1\metrics_by_seed_pool_budget.csv`

读出任务状态、CARR固定筛选`HGBC_a30`/Logistic/Threshold的均值，以及CTW的`GlobalStacking`在pool×calibration_budget下3种spot级随机划分的mean/min/max。**此记录转录的是用户终端摘要，不是助手已收到/逐行复核原始CSV**。

## CARR：12个子任务均success

| job | base_method | status | elapsed_seconds |
|---|---|---|---:|
| marker_k20 | RCTD | success | 175.385 |
| marker_k80 | RCTD | success | 169.650 |
| confusion_k1 | RCTD | success | 175.042 |
| confusion_k5 | RCTD | success | 184.844 |
| no_depth | RCTD | success | 187.534 |
| logistic_threshold | RCTD | success | 126.624 |
| marker_k20 | CARD | success | 170.941 |
| marker_k80 | CARD | success | 180.092 |
| confusion_k1 | CARD | success | 170.402 |
| confusion_k5 | CARD | success | 120.672 |
| no_depth | CARD | success | 120.850 |
| logistic_threshold | CARD | success | 89.929 |

CARR关键配置：
| job | base_method | method | target_RMSE | balanced_AUPRC | recall_at_10pct_FPR |
|---|---|---|---:|---:|---:|
| marker_k20 | RCTD | HGBC_a30 | .032125 | .559223 | .148469 |
| marker_k80 | RCTD | HGBC_a30 | .032610 | .556373 | .142771 |
| confusion_k1 | RCTD | HGBC_a30 | .032857 | .553475 | .143198 |
| confusion_k5 | RCTD | HGBC_a30 | .032316 | .555621 | .145477 |
| no_depth | RCTD | HGBC_a30 | .032353 | .556174 | .140064 |
| logistic_threshold | RCTD | LogisticPresence12 | .035769 | .545969 | .137500 |
| logistic_threshold | RCTD | Threshold1D | .057922 | .541670 | .124537 |
| marker_k20 | CARD | HGBC_a30 | .032742 | .548711 | .135755 |
| marker_k80 | CARD | HGBC_a30 | .033048 | .543935 | .135399 |
| confusion_k1 | CARD | HGBC_a30 | .033783 | .545695 | .129808 |
| confusion_k5 | CARD | HGBC_a30 | .033042 | .543539 | .134117 |
| no_depth | CARD | HGBC_a30 | .032992 | .545304 | .137821 |
| logistic_threshold | CARD | LogisticPresence12 | .035322 | .543170 | .131125 |
| logistic_threshold | CARD | Threshold1D | .037406 | .551166 | .146118 |

先前严格类别留出Full标准配置（已存旧记录，读出精度5位）：RCTD HGBC_a30 RMSE .03236/AUPRC .55619/recall .14103；CARD HGBC_a30 RMSE .03297/AUPRC .54521/recall .13832。20 marker在两方法上RMSE/AUPRC均描述性好于40 marker，但不能把事后选出的20认定已在独立集选型验证；No-depth接近原配置。CARD Threshold1D检测AUPRC .551166 高于标准CARR a30 .54521，但RMSE明显更差：检测与定量权衡需保留。

## CTW：GlobalStacking 36配置汇总

| pool | budget | JSD mean | JSD min | JSD max | matrix_RMSE mean | min | max |
|---|---|---:|---:|---:|---:|---:|---:|
| expanded4 | 100 | .112653 | .111615 | .113365 | .049706 | .049642 | .049784 |
| expanded4 | 200 | .113074 | .112471 | .113497 | .049656 | .049618 | .049712 |
| expanded4 | 500 | .113528 | .112921 | .113962 | .049604 | .049594 | .049617 |
| expanded4 | all | .113403 | .113383 | .113431 | .049586 | .049579 | .049598 |
| full6 | 100 | .113114 | .112248 | .113589 | .049144 | .049114 | .049184 |
| full6 | 200 | .113271 | .112653 | .113625 | .049053 | .049028 | .049098 |
| full6 | 500 | .113634 | .113016 | .114005 | .049000 | .048993 | .049007 |
| full6 | all | .113531 | .113507 | .113544 | .048966 | .048960 | .048973 |
| strong2 | 100 | .115249 | .113226 | .116841 | .052765 | .052747 | .052799 |
| strong2 | 200 | .115636 | .114536 | .116674 | .052718 | .052699 | .052750 |
| strong2 | 500 | .116118 | .115783 | .116698 | .052693 | .052691 | .052696 |
| strong2 | all | .116177 | .116167 | .116185 | .052691 | .052686 | .052697 |

`CTW CONFIGURATIONS 36`为用户终端输出。所有36组是GlobalStacking对照，不是主论文CTW SoftOpt的36组。使用full6且all的JSD mean .113531，matrixRMSE .048966；expanded4且all JSD mean .113403较低，但RMSE .049586较高。候选方法增多可改善该配置下matrixRMSE，JSD不严格单调下降。3种seed为同一数据的重划分，不是3个独立生物样本。没有独立检验/p值/置信区间结果。

## 下一补实验

已从GitHub源代码核实旧CTW verifier主要选择`Proposed_SoftOpt_5foldCV`作为历史`Proposed_CV`，使用按cell type的SLSQP/非负权重，训练折内拟合。本项目新建[CTW matched-fold批处理](../../CTW-RF/experiments/ctw_matched_fusion_comparisons_batch.py)，固定3 seeds × 3方法池，全局stacking/等权/HardSelect/InvRMSE_p2/CTW SoftOpt及原单方法**在完全相同5折**输出配对指标；脚本代码已经GitHub提交，**未在用户Windows同步或运行**。

用户要求实验扩充先行，完成后统一交Claude做整体方法/泄漏/论文审计。下一动作Windows按一条PowerShell同步并`--dry-run`，通过后另一条`--run`。不要重跑上述48个已有任务。
