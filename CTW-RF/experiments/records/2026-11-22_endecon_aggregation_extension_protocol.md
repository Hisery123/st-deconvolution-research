# 2026-11-22 CTW-RF补实验：EnDecon作者算法融合核心轻量对照

## 用户决定

用户要求先批量完成论文补实验，最终方法/论文全面审计交Claude统一审查；故优先复用已经存在的六种反卷积预测矩阵，不下载或重新安装完整依赖环境。

## 文献与作者实现（已直接核实）

- Tu, J.-J., Li, H.-S., Yan, H., Zhang, X.-F., 2023. *EnDecon: cell type deconvolution of spatially resolved transcriptomics data via ensemble learning*. *Bioinformatics* 39(1), btac825. DOI [10.1093/bioinformatics/btac825](https://doi.org/10.1093/bioinformatics/btac825).
- 官方作者代码 [Zhangxf-ccnu/EnDecon/R/EnDeconv.R](https://github.com/Zhangxf-ccnu/EnDecon/blob/master/R/EnDeconv.R) 实际读取其第1251–1309行 `solve_ensemble()`：
  - 初始化为基础预测均值；
  - `lambda = median(L1` distance of base matrices to mean`)`；
  - 每轮按`exp(-L1_distance/lambda)`更新全局方法权重，逐spot×celltype加权中位数更新组成预测；
  - 负熵正则的L1目标，目标函数**绝对变化**小于`1e-5`或最多100轮停止；
  - 最后将组成比例按行归一化。
- **特别注意：这不是另一个 [SunXQlab/EnDecon](https://github.com/SunXQlab/EnDecon) 的线性加权版实现。** 不应把不同作者的同名代码混用。

## 本次创建的实验脚本

[ctw_endecon_aggregation_batch.py](../ctw_endecon_aggregation_batch.py)已提交GitHub **但Windows尚未同步/运行**。该脚本是按作者公式及官方R核心实现编写的**Python融合阶段移植版**；不是直接运行作者R包，更不是重做原论文所调用全部14个基线模型。等价性包括默认lambda、更新方程、损失及终止条件；当加权累计权重恰好为0.5时，Python选择较小中位数，可能与R `spatstat.geom::weighted.median`在边界情形不同，不能宣称数值完全等价。

- 输入：与前两次CTW批实验相同`self_benchmark_cortex_svz_2000spots`2000spot×19celltype、6个已有基础反卷积输出；复用`global_stacking_cv.py`统一列对齐与行归一化。
- 3个嵌套方法池：strong2、expanded4、full6；3个不使用真值拟合的融合方法：EnDecon加权中位数、普通坐标中位数、等权均值；3×3=9个融合指标结果。
- 额外读前一批CTW `CTWRF_matched_fusion_20261122_v1/summary_metrics_by_seed_pool.csv`，用相同pool的3seed CTW SoftOpt和GlobalStacking各做对照，共18配对描述性差值。
- EnDecon是无监督**transductive**方案，融合权重在全部目标spot的预测矩阵上学习，不使用真值；CTW的SoftOpt基于训练折真值、对留出折预测。两者监督信息与输入协议并非完全对称，必须明确标注。
- 结果统一输出新目录`D:\Research\STdeconv_benchmark\results\CTWRF_EnDecon_aggregation_20261122_v1`：`ensemble_metrics_by_pool.csv`、`endecon_weights_by_pool.csv`、`endecon_diagnostics_by_pool.csv`、`ctw_matched_seed_comparisons.csv`、`predictions/`与`run_config.json`。不覆盖非空结果。
- 项目总控科学红线继续遵守；尚无此对照的实际结果，不得声称跑通或CTW优于EnDecon。
- 脚本最初版本已在助手容器`py_compile`静态语法检查（容器不包含研究者真实Windows输入；Python移植的R数值等价性仍未测试）。

## 下一步人工操作

用户一条PowerShell将GitHub `git pull --ff-only` 和新脚本`--dry-run`串起来（仅在拉取成功后才触发dry-run）；成功后下一轮单独`--run`一键完成整批。实际失败时保留本机输入/旧输出，不执行覆盖或强制重置。

完成后还有原计划第二平台/seqFISH+参考训练到留出FOV泛化、CTW DLPFC扩展等补实验，均属于待完成，不能提前写为完成。
