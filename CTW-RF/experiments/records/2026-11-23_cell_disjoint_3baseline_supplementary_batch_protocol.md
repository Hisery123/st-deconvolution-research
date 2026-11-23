# 2026-11-23 CTW-RF参考细胞/伪spot来源细胞无交叉：补充3基线实验脚本，待Windows预检/运行

## 本次成果状态

[CODE_COMMITTED_NOT_RUN] 已将[ctw_cell_disjoint_reference_batch.py](../ctw_cell_disjoint_reference_batch.py)提交研究GitHub。**用户Windows尚未pull、dry-run或run，新实验完全无实测指标。** 这不是旧6方法池全量重跑：旧版Tangram/RCTD/CellDART/CARD/cell2location/SPOTlight的完整运行入口和跨环境依赖未包含在当前研究仓库源快照。本次增量对照只使用在现有环境/已确认脚本下能够自洽计算的3种真正重新生成的基础方法，不能混用历史有重叠reference的数据预测，也不能称做历史六法公平复现。

## 实验方案（冻结于脚本）

- 基础数据：`D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz\sc_reference_counts.csv`与`sc_reference_labels.csv`，而**不是有同细胞重叠的旧`self_benchmark_cortex_svz_2000spots`输入/预测**。脚本按单细胞类别随机划分ID，约50%为mapping reference；剩余分为train donor与test donor，三组cell IDs严格不相交。
- 小类边界：单例留给reference，两个细胞的类别留1个reference+1个train donor，test donor为0；脚本记录每类计数以及没有训练/测试donor的细胞类型。不承诺每个类均在独立测试出现。
- 两种采样情景固定：`balanced_celltype`（按类别均衡抽样）与`cell_uniform`（按实际donor细胞频数抽样）。每情景从**train donor**生成1200个8-cell合成spot，从**test donor**生成800个8-cell合成spot。每个pseudo spot可重复抽到同一细胞，来源细胞在各自组内跨spot重复；**不同组donor ID不重叠**。不把生成的spot当独立供体。
- 重新运行三个基础方法：Tangram（用户已确认的`D:\ProgramData\miniconda3\envs\Tangram\python.exe`环境，`run_tangram_self_benchmark.py`，500epoch，3000genes，mode=cells，density_prior=rna_count_based；train/test分别映射，共4次）；`NNLS_500`（reference总丰度最高500genes）；`NNLS_marker20`（每细胞类按reference-only富集选择最多20marker，合并去重；真正`scipy.optimize.nnls`求非负分量）。三基线均使用完全同一个mapping reference池。
- 直接复用此前`global_stacking_cv.py`的全局非负权重和评价，以及`ctw_matched_fusion_comparisons_batch.py`的CTW HardSelect、InvRMSE_p2、SoftOpt SLSQP实现。训练**仅使用train donor伪spot真值**，预测/评价在test donor伪spot，主方法是`CTW_SoftOpt`，同时报全部3基线、EqualWeight、GlobalStacking、HardSelect、InvRMSE_p2共8方法×2情景=16行。负结果不筛掉。
- 测试伪spot真值仅用于测试指标计算，所有参与基线拟合的基因/谱筛选依赖reference；Tangram train/test映射可用各自未知组成的表达特征，因此属于转导式基础映射。
- 结果写入独立`D:\Research\STdeconv_benchmark\results\CTWRF_cell_disjoint_20261123_v1`，包括source cell ID三组划分表、每情景train/test各自输入、成员来源表和真值、Tangram日志、3基线预测、各CTW测试预测、权重和`metrics_by_sampling_scenario.csv`。拒绝覆盖非空输出；`--resume`需配置完全相同且会检查现有输入与预测。
- `--dry-run`不写任何文件：检查数据存在、细胞拆分、Tangram独立Python模块导入、两种采样各6个伪spot以及小规模NNLS输出；正式训练只允许用户明确执行`--run`。

## 科学定位和限制

- 这是**旧CTW-RF六方法研究的补充参考细胞无交叉测试**，不是六方法主实验重训；候选基础池变化意味着不能直接将其均值与旧6方法表作为唯一变量对照，更不能由3相关baseline推断通用集成创新性。
- 原始single-cell仍来自同一个cortex-SVZ空间细胞来源，测试donor ID与训练/reference不重叠，但**不是独立实验平台/动物/供体**；统计上pseudo spots仍重用donor cell，不能视为800个独立生物重复。
- 外部真实数据验证和旧6方法严格无重叠重算仍属未完成工作；用户要求先批量补实验，最后Claude集中审计。

## 用户下一唯一动作

先用PowerShell一条组合命令拉GitHub，成功才用`python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_cell_disjoint_reference_batch.py" --dry-run`。出现`SMOKE PASS`两次与`DRY RUN PASS — no files written`方可下一步`--run`；报错只贴日志，不删结果目录。
