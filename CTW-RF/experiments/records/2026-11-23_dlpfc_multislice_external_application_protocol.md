# 2026-11-23 CTW-RF DLPFC多切片真实Visium应用批处理：脚本已提交，Windows待预检

## 证据和任务

[USER_WINDOWS_DIRECTORY_LIST] 用户本机已显示：
- `D:\Research\real_DLPFC\candidate_inputs\` 包含`reference_70_expression_logcounts.csv`, `reference_70_labels.csv`, `real_visium_expression_counts.csv`, `real_visium_spot_metadata.csv`及logcounts；
- `D:\Research\real_DLPFC\candidate_predictions\real_visium\`已有CARD、CellDART、RCTD、SPOTlight、Tangram等**历史某一真实Visium切片预测**，但尚未确定它们覆盖全部12张，不能声称多切片已有全部六个基础方法结果；
- `D:\paper\ST_Benchmark_Planning\mvp\data\`前30项有151507/151508/151509/151510的`filtered_feature_bc_matrix.h5`与`manual_layer_annotations.csv`或`spots_aligned.csv`，**仅看到这四项，其他目标切片是否存在由脚本自动发现，不能预称12张完整可用**。
- Fusion目录三个旧融合脚本，不作为新多切片推断器（历史常量固定2000spot pseudo benchmark）。

[CODE_COMMITTED_NOT_RUN] 新建[CTW-RF 真实DLPFC多切片应用脚本](../ctw_dlpfc_multislice_application_batch.py)，**尚未被用户Windows pull/dry-run/run；没有新切片预测结果**。

## 一键批处理冻结流程

1. 在12个目标ID（151507–151510、151669–151676）中自动发现实际存在的10x filtered H5，读取HDF5 feature names/barcode；读`reference_70_expression_logcounts.csv`和`reference_70_labels.csv`按细胞ID对齐，取所有发现切片与单细胞参考共有基因，不用真值预测目标组成。每张切片读取其表达矩阵，只提取共有基因。
2. 同一参考细胞按类型随机拆成约50% profile reference / 30% synthetic-train donor / 20% synthetic-holdout donor，source cell ID互斥。训练600个8细胞synthetic pseudo spot、内部检验200个，都是参考同源合成增强，**不是独立供体**。与真实Visium的train/test不混称。
3. 对训练合成spots及真实Visium使用同一套profile-reference细胞群、三种预冻结NNLS变体：`NNLS_all`（所有共有基因）、`NNLS_top300`（只按reference表达强度选前300）、`NNLS_marker20`（每type只按reference profile富集选最多20）。与历史六法实验不同，**不可把这一批称历史六法扩到12张切片**。
4. 用synthetic训练真值固定拟合全局非负stacking、CTW HardSelect、InvRMSE_p2和SoftOpt权重，对全部发现切片只应用固定权重，导出3基础+5融合=8种方法×slice预测。Synthetic holdout有`synthetic_donor_holdout_metrics.csv`，但真实Visium**没有**组成真值，因此不计算或宣称真实spot上的JSD/RMSE/accuracy。
5. 每张切片自动从`manual_layer_annotations.csv`或`spots_aligned.csv`识别barcode及L1–L6/WM，并存每类型分层预测均值、覆盖spot数、各方法完整spot×type预测；无分层标签时记录`NO_LAYER_LABELS`并仍导出表达预测。不编造不存在的分层；有Oligo类时额外记录`WM−cortex`差值，为定性/间接的生物预期指标，不是真值。
6. 全部结果写到新独立目录`D:\Research\STdeconv_benchmark\results\CTWRF_DLPFC_multislice_20261123_v1`，含`run_config.json`、`frozen_fusion_weights.csv`、`synthetic_donor_holdout_metrics.csv`、各slide预测、`slide_coverage_summary.csv`、`all_slide_layer_celltype_means.csv`。有非空目录时`--run --resume`匹配配置并重用已经写全的切片，不覆盖历史任务。给新数据跑完后再Claude集中全审。

## 下一用户唯一操作（不写盘）

```powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only; if ($LASTEXITCODE -eq 0) { python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_dlpfc_multislice_application_batch.py" --dry-run }
```

预期打印`PREFLIGHT reference_cells...shared_genes_all_slides...slides_found...`、自动发现切片详情、`SMOKE PASS 4 synthetic spots 3 NNLS methods`和`DRY RUN PASS — no files written`。如果`h5py`缺失、sc ref IDs不匹配、共用基因不足、某个slide HDF5不是10x矩阵，贴原始报错，直接修复批处理不让用户碎片化审核。预检成功后下一轮才执行`--run`。
