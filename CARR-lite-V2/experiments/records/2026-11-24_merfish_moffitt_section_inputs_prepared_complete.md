# 2026-11-24 MERFISH Moffitt 五个真实空间切片留出输入已正式准备成功

## 用户 Windows 原始终端证据 [USER_WINDOWS_RUN]

```text
SOURCE 73655 cells 161 genes animals 1 sections 12 ambiguous 9282
X SAMPLE {'sample_min': 0.0, 'sample_max': 234.93914794921875, 'sample_noninteger_positive_fraction': 0.3899296066252588, 'n_animals': 1, 'n_sections': 12, 'n_classes_including_ambiguous': 16, 'n_ambiguous': 9282}
TEST SECTIONS [-28.999999999999996, -14.000000000000002, -4.0, 11.0, 26.0] indices [0, 3, 5, 8, 11]
FOLD READY 0 Bregma -28.999999999999996 reference 1685 true_spatial_bins 350 n_classes 15 unknown_in_bins 544
FOLD READY 1 Bregma -14.000000000000002 reference 1683 true_spatial_bins 350 n_classes 15 unknown_in_bins 340
FOLD READY 2 Bregma -4.0 reference 1681 true_spatial_bins 350 n_classes 15 unknown_in_bins 331
FOLD READY 3 Bregma 11.0 reference 1681 true_spatial_bins 350 n_classes 15 unknown_in_bins 398
FOLD READY 4 Bregma 26.0 reference 1676 true_spatial_bins 350 n_classes 15 unknown_in_bins 418
PREPARATION FINISHED 5 held-out sections
OUTPUT D:\Research\STdeconv_benchmark\data\external\MERFISH_Moffitt_2018\carr_sections_v1
NO MODEL TRAINING DONE
```

用户曾在更早一次`--prepare`得到`FileExistsError: Refuse existing output; no silent fold overwrite`，但最新用户Windows终端已经明确成功`PREPARATION FINISHED`。以最新版成功日志为准，不将旧失败当作现有阻塞。不猜测此前目录为何非空，不能据此认定手动清理或其他状态。

## 已完成与尚未完成

- [INPUT_PREP_COMPLETED] 5个`held_out_FOV0..4`输入数据文件生成（根据脚本合同：`pseudo_spot_expression.csv`、`pseudo_spot_locations.csv`、`sc_reference_counts.csv`、`sc_reference_labels.csv`、`pseudo_spot_ground_truth.csv`、`pseudo_spot_ground_truth_counts.csv`、`synthetic_spot_membership.csv`、`spatial_source_trace.json`），`run_config.json`与`section_holdout_manifest.csv`应写入输出根；尚未经用户单独读取文件完整性，但程序到达`PREPARATION FINISHED`证明写出循环无异常。
- [NO_MODEL_TRAINING_YET] 这一步未训练Tangram/CARR，也没有任何本次MERFISH持出测试JSD/AUPRC/RMSE。**不要宣称外部模型验证已完成**。
- [RESEARCH_BOUNDARIES] 新研究/测量技术来源，12切片但`Animal_ID=1`；总计1750空间bins属于一只动物，绝不是1750独立生物样本；标签来源作者`Cell_class`，排除`Ambiguous`，真值仅相对于可明确标注细胞的bin比例；表达由原预处理MERFISH X按来源细胞加和，不是原始分子整数count。
- [FROZEN] 测试切片分箱由输入几何预先确定，绝不根据结果重选fold/调阈值；已有CTW六方法24/24结果冻结，不重跑。

## 下一任务：只读预检匹配CARR 5折原runner

脚本`CARR-lite-V2/experiments/carr_reference_only_seqfishplus_batch.py`已在GitHub，默认原seqFISH+跑法不变，添加可选`--density-prior uniform`适用于MERFISH预处理强度；本次跨来源实验必须给独立`--data-root`和新`--out-dir`、Tangram Conda解释器真实绝对路径：
```powershell
& "D:\ProgramData\miniconda3\envs\cell2loc_env\python.exe" "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\carr_reference_only_seqfishplus_batch.py" --dry-run --data-root "D:\Research\STdeconv_benchmark\data\external\MERFISH_Moffitt_2018\carr_sections_v1" --out-dir "D:\Research\STdeconv_benchmark\results\CARR_MERFISH_Moffitt_sections_20261124_v1" --tangram-python "D:\ProgramData\miniconda3\envs\Tangram\python.exe" --density-prior uniform
```
此命令会检查5个fold CSV、CARR runner存在、Tangram环境能导入及source reference/generator分离，预计`DRY RUN PASS — no files written`，**不启动模型训练**。若Python环境导入或CSV读取错误，保留原日志，针对错误修复，不擅自开启训练。注意当前用户仍在Windows PowerShell手动操作，每次仅给一条可复制命令。
