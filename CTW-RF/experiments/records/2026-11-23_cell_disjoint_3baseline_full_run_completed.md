# 2026-11-23 CTW-RF来源细胞三组无交叉补充实验：Windows完整运行成功

## 真实状态与来源

[USER_WINDOWS_CONSOLE] 用户在Windows亲自执行：
```powershell
python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_cell_disjoint_reference_batch.py" --run
```
终端确实输出`BATCH FINISHED: 2 scenarios x 8 methods = 16 held-out method/scenario rows`。以下数值系用户原始控制台转录，不是助手获取本地结果文件后独立复算。

- 836 source cells、10,000 genes、19 types；reference 419、train donors 204、test donors 213；三组source cell IDs无交叉按脚本协议生成；L12/L16/L17/L4/L8无train/test donors，均只有参考细胞。
- Tangram基线使用独立Python环境（前序预检实测CUDA False），balanced train/test 60.04/42.43s，cell_uniform train/test 63.04/43.09s。单独Tangram训练和预测真实耗时为此日志值，不能推广为其它机型时长。
- SoftOpt fallback count=0，两场景各有8方法行。输出在`D:\Research\STdeconv_benchmark\results\CTWRF_cell_disjoint_20261123_v1`；此前历史结果目录未被覆盖。

## 16行用户控制台指标（六位小数）

```csv
scenario,method,JSD,matrix_RMSE,aggregated_celltype_RMSE
balanced_celltype,EqualWeight,0.264094,0.084731,1.424977
balanced_celltype,GlobalStacking,0.263915,0.084946,1.420992
balanced_celltype,CTW_HardSelect,0.275713,0.087957,1.432274
balanced_celltype,CTW_InvRMSE_p2,0.249645,0.084144,1.371191
balanced_celltype,CTW_SoftOpt,0.254912,0.083280,1.348836
balanced_celltype,Tangram,0.300133,0.100277,1.535962
balanced_celltype,NNLS_500,0.313419,0.097729,1.675692
balanced_celltype,NNLS_marker20,0.298360,0.094462,1.606819
cell_uniform,EqualWeight,0.174313,0.070640,1.106366
cell_uniform,GlobalStacking,0.146024,0.062554,0.966025
cell_uniform,CTW_HardSelect,0.143822,0.062960,0.970411
cell_uniform,CTW_InvRMSE_p2,0.152765,0.065254,1.002648
cell_uniform,CTW_SoftOpt,0.143227,0.062353,0.959604
cell_uniform,Tangram,0.144009,0.062958,0.969367
cell_uniform,NNLS_500,0.237648,0.091882,1.430940
cell_uniform,NNLS_marker20,0.234839,0.087339,1.361953
```

## 描述性结论与必须保留的负结果

- balanced：SoftOpt JSD .254912 优于Global .263915（差-0.009003）、EqualWeight .264094、Tangram .300133；但**CTW_InvRMSE_p2 JSD .249645更好**，SoftOpt非JSD最佳；SoftOpt矩阵RMSE .083280与agg_RMSE 1.348836为该场景八法最低。
- cell_uniform：SoftOpt JSD .143227、matrixRMSE .062353、agg_RMSE .959604，在该场景八法中最低。但JSD相对Tangram .144009只低.000782、相对Global .146024只低.002797；矩阵RMSE对Global只低.000201，效应很小，不能夸大。
- 自然频率采样与均衡采样数值差异明显，但**两情景类别组合与目标分布不同**，不把差异归因于单变量方法效果或当独立生物学重复。
- 本批是**重新训练的三个基础方法 Tangram/NNLS_500/NNLS_marker20**，不是历史六方法完整无交叉复跑，不能与旧六方法版本进行唯一变量因果比较。
- 模拟训练/测试spot在各自donor细胞池中有重复抽样；三种细胞池虽然source cell ID不重叠，仍来自同一cortex-SVZ领域，不是跨平台/跨动物独立验证。五个少数类别只有reference pool、truth为零，不应事后隐瞒。
- 尚未做正式论文全链路数据审计、独立来源统计显著性、或为这批专门重新训练原RCTD/CARD/cell2location/SPOTlight/CellDART。

## 下一任务

尊重用户“继续按计划执行，最终再审计”的明确要求，**本批结果冻结，不继续审核或调参**。进入CTW的DLPFC多切片应用，寻找本机已经存在的真实DLPFC数据及输入运行脚本，优先复用既有代码；首次只需一条只读命令列文件清单，不要求用户做多轮检查或手动跑单个切片。
