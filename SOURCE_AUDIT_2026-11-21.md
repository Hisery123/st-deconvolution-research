# 2026-11-21 GitHub source-snapshot 只读审计（阶段 1）

> 本次只检查远端仓库代码文本和历史 CSV 的部分内容；**未在研究者的 Windows 电脑执行脚本、未下载原始数据、未用 CSV 独立复算模型性能**。以下分离【代码直接确认】与【潜在方法学风险】。审计时仓库为公开仓库。

## 1. 归档来源与范围

- 远端提交：[5666894905eb7e49d83158fbbcaf88e92ed8a03c](https://github.com/Hisery123/st-deconvolution-research/commit/5666894905eb7e49d83158fbbcaf88e92ed8a03c)
- API 返回 **62 个新增文件**：CTW-RF **53** 个、CARR-lite V2 **9** 个；扩展名分布：14 个 `.py`、46 个 `.csv`、2 个 `.md`。
- [代码/README] CTW 来源自 Windows `D:\Research\STdeconv_benchmark` 的部分原始文件；CARR 来源自 `D:\Research\TRUST_Deconv`。路径只由归档说明报告，当前没有直接检查用户 Windows 磁盘。
- [README] 两项均为历史 snapshot，原始输入数据、逐 spot 预测、完整环境/依赖/第三方源码未随本次提交归档，不能称“完整可复现”。
- 文件名检查未见明显命名为 token/password 的文件；**未完成逐文件敏感信息和第三方许可审计**。公共仓库中的结果 CSV/脚本及 Git 历史可能包含路径或应受限制的信息，不因 `.gitignore` 存在就保证安全。

## 2. CTW-RF：参考细胞/伪 spot 可能重用（阻断风险 1）

**直接证据**：
- `CTW-RF/source-snapshot/data/groundtruth/self_benchmark_cortex_svz_2000spots/build_self_benchmark_2000spots.py`：
  - 从 `sc_reference_counts.csv` 与 `sc_reference_labels.csv` 对齐 `common_cells`。
  - 逐 pseudo-spot 从这批细胞中抽取若干细胞表达生成表达矩阵与比例真值（约第 217–260 行）；默认 `SAMPLING_MODE = "balanced_celltype"`、`N_MIX_CELLS = 8`。
  - 后续直接导出**相同对齐后细胞集合**为新目录的 `sc_reference_counts.csv` 与 `sc_reference_labels.csv`（约第 326–341 行）；脚本中没有看见参考/造 spot 的细胞级拆分。
- **判定**：生成器的参考文件与伪 spot 来源细胞不隔离，是代码层面已观察事实。是否造成每个基础反卷积器的实际泄漏，还要确认其参考输入确实使用此导出集、并核对完整运行日志。**不能仅凭生成器就断言全部历史基线已泄漏、历史结果无效**。

**建议**：先寻找各基础方法实用参考文件的启动脚本/配置。若确实重用，冻结一份不交叉的细胞拆分方案、重新生成 pseudo-spot、重新执行相关基线与融合，再评估。

## 3. CTW-RF：交叉验证权重与最终模型选择（阻断风险 2）

**直接证据**：
- `CTW-RF/source-snapshot/methods/Fusion/run_reliability_fusion_2000spots.py` 的 `build_cv_variant`（约 556–612 行）：
  - 每折 `train_idx` = 全部 spot 减去 `test_idx`；
  - 调用对应的权重学习方法，仅用 `train_idx` 的真值学习权重；
  - 将融合结果写回当前折 `test_idx`。**从这段代码看，单次五折融合权重遵守 spot 级留出**。
- 但 `save_all_outputs`（约 683–699 行）在对含 full-fit 与 CV 版本的指标表进行评价后，以整体 `total_RMSE`、`JSD` 选择 `Proposed_best_self_benchmark.csv`；`evaluate_predictions` 在同一数据上算指标。**这不是独立外部测试的最佳版本选择**。
- `CTW-RF/source-snapshot/evaluation & visualization/reliability_fusion_2000spots/figures/verify_cv_reliability_fusion_2000spots.py` 另有明确五折验证逻辑（约 301–346 行），但同样不能替代未接触的最终测试。

**判定**：内部 CV 权重拟合与“跨模型版本选择后的无偏泛化误差”是两回事；还需区分 full-fit 的训练内表现与 CV 指标。若把在相同数据上选中的最优方法的 CV 表现当作完全独立最终测试，会存在选择偏差风险。

**建议**：提前冻结选型方法/目标指标，或增加外层嵌套划分（nested CV）/独立数据进行最终评价；full-fit 只用于最终部署模型/训练集表现，不与 OOF 指标混报。

## 4. CARR-lite V2：部署时未知的深度特征（阻断风险 3）

**直接证据**：
- `CARR-lite-V2/source-snapshot/CARR_lite_v2/carr_lite_tangram.py` 在 `build_dataset` 中构建第 12 项 `depth_fraction = int(depth) / 100.0`（约 136–167 行）。
- `CARR-lite-V2/source-snapshot/CARR_lite_v2_52scenario/carr_lite_v2_52scenario.py` 在构建模拟视图时使用 `int(depth_from_scenario(scenario_id)) / 100.0`（约 122–151 行），同样依赖已知的受控模拟深度标签。
- 它**不直接使用测试比例真值**作为预测输入；风险是对实际未知深度/平台状态的部署适用性不足，不能未经说明直接外推。

**建议**：预先定义仅在受控模拟下可用的条件特征，并设计移除 `depth_fraction` 的成对公平对照；如果要替代该特征，应限定为实际可从观测读数计算的变量，不用测试真值推导。

## 5. CARR-lite V2：已具备的分组留出结构（正面发现）

- `CARR-lite-V2/source-snapshot/CARR_lite_v2_52scenario/carr_lite_v2_52scenario.py` 约第 293–315 行：对 `bases` 每次留出一个完整 base，将该 base 全部深度视图放入测试，其余 base 训练，代码层面确有 **leave-one-base-out / 13-fold** 结构。
- `CARR-lite-V2/source-snapshot/CARR_lite_v2/carr_lite_tangram_v2.py` 约第 97–109 行亦对 `held_out` base 分离训练/测试。
- **尚未验证**不同 base 是否共享细胞、target subtype 或源数据；不能仅依据名字/逻辑认为是独立生物学重复；也不能称其已经覆盖独立真实 FOV / 新平台。
- 原 `carr_lite_v2_summary.csv` 和 `carr_lite_v2_metrics_by_fold.csv` 是历史导出，包含部分正向及负向差异。运行和复算尚未完成。

## 6. 核实的历史 CSV（不是本次复算）

- `CTW-RF/.../reliability_fusion_2000spots_cv_verify/03_main_cv_comparison.csv` 中 `Proposed_CV` 行报告 JSD `0.1017517246`、`aggregated_celltype_RMSE` `0.7256698232`；`cell2location` 的 JSD `0.0989963461`。说明指标定义和不同目标下的最优方法需要分别讨论。
- `CARR-lite-V2/.../carr_lite_v2_results/carr_lite_v2_metrics_by_fold.csv` 中部分方法虽降低 target_RMSE，但 `balanced_AUPRC` 和 `recall_at_10pct_FPR` 在一些配置/折中下降；必须报告所有预先定义的指标和负结果。
- 这些数字只能证明远端 CSV 有对应数值，不等于方法性能已被第三方复算或可跨数据泛化。

## 7. 下一步建议（未执行）

1. **先 CTW 的数据来源隔离审计**：取得至少一个实际基础方法（如 CARD、Tangram）的运行入口，核对它读的是哪份参考文件，整理 source-cell ID 与 pseudo-spot constituent cell ID。若构成细胞 ID 未保存，需要在修复构造脚本时增设追溯记录。
2. 然后冻结 CTW 的无重叠细胞级划分、外层测试/选型规则和最近邻集成方法对照；不先盲目重跑所有模型。
3. CARR 的 `depth_fraction` 移除及按 base 隔离敏感性实验应与 RCTD/CARD 扩展并行规划，但后续用户 Windows 执行仍一次只提供一个命令/短步骤。

**仅完成代码静态审计，不代表修复、复现、实验运行或论文修订已经完成。**
