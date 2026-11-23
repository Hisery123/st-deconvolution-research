# 2026-11-23 CTW-RF DLPFC多切片真实Visium应用：全部12张正式完成（Windows终端）

## 证据层级和实验状态

[USER_WINDOWS_RUN_STDOUT] 用户Windows同步GitHub当前DLPFC脚本（包含NNLS有限面板零解回退、零共有基因总表达spot排除），执行`ctw_dlpfc_multislice_application_batch.py --dry-run --resume`后自动执行`--run --resume`。Dry run出现`FALLBACK SMOKE PASS 2 fallback rows`、`ZERO-SPOT SMOKE PASS valid 2 excluded 1`、`DRY RUN PASS — no files written`，正式run最终成功：

```text
PREFLIGHT reference_cells 6997 cell_types 7 shared_genes_all_slides 539 slides_found 12 expected 12
CELL SPLIT {'reference': 3499, 'train_donor': 2098, 'check_donor': 1400}
CALIBRATION synthetics checked; SoftOpt fallback 0 metrics not a real Visium ground-truth test
REUSE COMPLETED SLIDE 151507
...
BATCH FINISHED 12 DLPFC slices; 96 slice-method prediction matrices
OUTPUT D:\Research\STdeconv_benchmark\results\CTWRF_DLPFC_multislice_20261123_v1
```

**本记录数字转录自用户本地终端，并非助手独立下载原始CSV字节。** 测试真实Visium不存在真实cell-type compositional ground truth，不能据此声称更低的Visium JSD/RMSE。此前两次中断的负状态保留：[零marker面板首次失败](2026-11-23_dlpfc_first_run_marker20_zero_fallback_fix.md)和[151508零共有基因spot中断](2026-11-23_dlpfc_151508_zero_shared_genes_resume_fix.md)。

## 12张切片真实完成摘要

| slide | H5 spots | predicted spots | layer labeled predicted | NNLS_marker20 fallback | zero shared-gene excluded |
|---|---:|---:|---:|---:|---:|
| 151507 | 4226 | 4226 | 4221 | 69 | 0 |
| 151508 | 4384 | 4383 | 4380 | 101 | 1 |
| 151509 | 4789 | 4789 | 4788 | 80 | 0 |
| 151510 | 4634 | 4633 | 4594 | 76 | 1 |
| 151669 | 3661 | 3661 | 3636 | 40 | 0 |
| 151670 | 3498 | 3498 | 3484 | 52 | 0 |
| 151671 | 4110 | 4110 | 4093 | 54 | 0 |
| 151672 | 4015 | 4015 | 3888 | 45 | 0 |
| 151673 | 3639 | 3639 | 3611 | 13 | 0 |
| 151674 | 3673 | 3673 | 3635 | 4 | 0 |
| 151675 | 3592 | 3592 | 3566 | 24 | 0 |
| 151676 | 3460 | 3460 | 3431 | 13 | 0 |
| **合计** | **47681** | **47679** | **47327** | **571** | **2** |

- 仅151508与151510各有1个在539共通基因上总表达为零的spot，因此没有编造其细胞比例；脚本将spot_id写入相应`zero_shared_gene_excluded_spots.csv`。
- NNLS_marker20共571个/47679个可预测spot（1.1976%）因有限gene panel得到零解而回退至同spot的全539gene NNLS。NNLS_top300的实测回退为**0**。这些fallback是透明的数值补救，不应解释为独立的marker20成功预测。
- 151507在首次修复后已完成，成功resume时**REUSE COMPLETED SLIDE 151507**，未重新处理已完成该片。其余11片完成。
- 预测矩阵 = 每slice 3种参考式NNLS基础法（NNLS_all、NNLS_top300、NNLS_marker20，含回退）+ 5种融合/对照（EqualWeight、GlobalStacking、CTW_HardSelect、CTW_InvRMSE_p2、CTW_SoftOpt）= 8×12=96个spot×7 cell-type矩阵，不是96个独立实验。
- 通过同一参考细胞6997 cells / 7 labels /539共用genes建参考profile，独立单细胞ID拆成profile 3499、synthetic train donor2098、synthetic check donor1400，在合成check spot评估（无SoftOpt optimizer fallback），冻结权重后应用真实Visium。此项**不是历史六法的12slice版本**，不是跨平台组成真值评价。
- 每张切片真实空间层标注来自`manual_layer_annotations.csv:layer`，合计47327个预测spot有匹配层标签，可用于描述性层富集分析，但层标签不是真实细胞比例。
- 正式运行完整结果：`D:\Research\STdeconv_benchmark\results\CTWRF_DLPFC_multislice_20261123_v1`，主要包括`slide_coverage_summary.csv`, `all_slide_celltype_means.csv`, `all_slide_layer_celltype_means.csv`, `frozen_fusion_weights.csv`, `synthetic_donor_holdout_metrics.csv`，各slice目录的8种预测、匹配layer、回退诊断、零spot清单和summary JSON。

## 后续执行

按用户最新偏好：**先完成其余实验，最后由Claude系统审计/统计/写作**，此已完成DLPFC新批锁定、不重跑不继续碎片审核。下一步可优先准备旧CTW-RF六原始baseline严格无重叠reference重跑，需找到本机实际各原始方法的runner入口；如果不可获得，则不冒充完整重跑，转其他独立数据CARR/CTW外部实验。
