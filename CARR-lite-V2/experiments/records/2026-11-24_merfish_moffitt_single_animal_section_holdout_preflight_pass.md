# 2026-11-24 Moffitt真实MERFISH：5个跨切片留出外部验证预检已全部PASS

## 用户Windows原始日志 [USER_WINDOWS_STDOUT]

```text
SOURCE 73655 cells 161 genes animals 1 sections 12 ambiguous 9282
X SAMPLE {'sample_min': 0.0, 'sample_max': 234.93914794921875, 'sample_noninteger_positive_fraction': 0.3899296066252588, 'n_animals': 1, 'n_sections': 12, 'n_classes_including_ambiguous': 16, 'n_ambiguous': 9282}
TEST SECTIONS [-28.999999999999996, -14.000000000000002, -4.0, 11.0, 26.0] indices [0, 3, 5, 8, 11]
FOLD READY 0 Bregma -28.999999999999996 reference 1685 true_spatial_bins 350 n_classes 15 unknown_in_bins 544
FOLD READY 1 Bregma -14.000000000000002 reference 1683 true_spatial_bins 350 n_classes 15 unknown_in_bins 340
FOLD READY 2 Bregma -4.0 reference 1681 true_spatial_bins 350 n_classes 15 unknown_in_bins 331
FOLD READY 3 Bregma 11.0 reference 1681 true_spatial_bins 350 n_classes 15 unknown_in_bins 398
FOLD READY 4 Bregma 26.0 reference 1676 true_spatial_bins 350 n_classes 15 unknown_in_bins 418
DRY RUN PASS — no files written; no model training
```

## 记录解释与限制

- 源数据73,655 cells ×161 measured genes，12个Bregma切片、**一个动物**；5预定holdout切片均能生成350个来自真实细胞坐标的空间格网bin（总1750测试bin，仅技术/空间单位，绝不可当1750个生物学重复），每折有约1676–1685个参考细胞及15个确信类别；排除Ambiguous 9282元细胞，目标bin内未知细胞数量每折544/340/331/398/418。研究使用作者注释构造 **annotation-derived composition truth among non-Ambiguous cells**，预处理表达非raw RNA molecule counts，且构造bin时在模型输入中排除了Ambiguous来源细胞，论文必须如实说明其为标签筛选的benchmark构建而非native mixed assay。
- [DRY_RUN_ONLY] 表明几何和源矩阵在本机检查通过；尚**没有准备写盘、没有Tangram/CARR训练或外部指标**，未做GPU测试，不可宣称独立动物验证完成。
- 下一用户唯一PowerShell步骤：运行已同步脚本`& "D:\ProgramData\miniconda3\envs\cell2loc_env\python.exe" "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\prepare_merfish_moffitt_external_sections.py" --prepare`。只生成`D:\Research\STdeconv_benchmark\data\external\MERFISH_Moffitt_2018\carr_sections_v1\held_out_FOV0..4`里的预测输入CSV和有评测真值的CSV，并记录分箱成员与来源，**不训练**。预计`PREPARATION FINISHED 5 held-out sections`、`NO MODEL TRAINING DONE`。若输出目录已非空则原脚本拒绝覆盖，保留报错，不删除任何文件。
- 准备成功后下一批使用已有`carr_reference_only_seqfishplus_batch.py`，带`--data-root`对应外部输入和单独`--out-dir`，可选`--density-prior uniform`适配预处理MERFISH；Tangram环境显式独立解释器，用`--dry-run`首检，再`--run`，**不得**在数据准备成功前认定模型能跑或结果有效。
- user研究习惯：每次Windows仅一条命令；先完成计划实验，再统一统计/创新性审计。异常时先报告日志，不臆测成功。
