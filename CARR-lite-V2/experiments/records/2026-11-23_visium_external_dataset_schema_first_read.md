# 2026-11-23 mouse-brain Visium候选外部应用：四CSV局部结构与来源线索首审

## 用户本地只读日志 [USER_WINDOWS_OUTPUT]

目录：`D:\Research\STdeconv_benchmark\data\visium`，用户用当前venv的pandas逐文件只读`nrows=2`：

| filename | MB (decimal) | csv总列数（含ID） | 方向/头部证据 |
|---|---:|---:|---|
| sc_mousebrain.csv | 2081.93 | 12820 | 首列Unnamed:0为`5705STDY8058285_GGTAGAGTCAAATAGG-1`等cell barcode ID；余列如Xkr4、Gm1992、Mrpl15、Tcea1、Rgs20；**cell×gene，基因数12819** |
| sc_celltype.csv | 1.77 | 2 | 首列cell barcode ID与sc_mousebrain前两行一致，`annotation_1`示例`Astro_AMY` |
| st_count.csv | 161.12 | 2577 | 首列是gene ID如Xkr4、Gm1992；其余2576列是Visium-style spot barcode如AAACAAGTATCTCCCA-1；**gene×spot，需转置为spot×gene** |
| st_location.csv | 0.07 | 3 | 首列spot barcode示例TCGGCTAACTTCCCTT-1，余列`row`/`col`坐标 |

仅从四个CSV的大小/表头与前两行，可确认参考单细胞表达、类型标注、空间表达、坐标四种结构存在；**不能由此确认完整基因交集、全体单细胞与标签ID吻合、spot与坐标ID匹配、切片样本/动物独立性及目标组成真值**。

## 公开来源核查 [EXTERNAL_WEB_HYPOTHESIS]

- cell2location官方文档[Spatial mapping of cell types across the mouse brain](https://cell2location.readthedocs.io/en/latest/notebooks/cell2location_estimating_signatures.html)描述其10x snRNA-seq与Visium小鼠脑数据来自相邻组织切片；[GitHub作者答复](https://github.com/BayraktarLab/cell2location/discussions/176)的样本匹配表确有`5705STDY8058285`，此为与当前sc ID同号的公开文献数据线索。
- **仍不能确定本机`st_count.csv`究竟对应哪一张ST样本，以及ref与ST是否同动物/同切片或不同来源**。不能断言本机该Visium文件已经具备真实ground-truth celltype proportion。
- 论文来源不宜直接把Visium结果称为新原创验证数据或稀有细胞定量真值；若最终无细胞组成真值，只能用定性空间映射/生物合理性+预先定义不依赖真值的质控。

## 后续最小只读完整性检查

用`pd.read_csv(sc_mousebrain,nrows=0)`取得sc基因列，`pd.read_csv(st_count,usecols=[0])`取得ST基因行，`pd.read_csv(st_count,nrows=0)`取得spot列，用`pd.read_csv(st_location,usecols=[0])`取得坐标spot ID和`sc_celltype.csv`取得标注类型数。**刻意不加载完整2.08 GB sc matrix**，先核实sc/st基因集合交集、spot/坐标数量重合与类型类别数；必要后续查样本ID/文件出处和与原历史研究关联。

## 评价约束

当前CARR reference-only seqFISH+ 5FOV数据已锁定，下一项Visium候选只是外部应用计划**尚未训练或评价**。Visium若无独立真实组成真值，不能拿CARR/Tangram/CARD预测的一种作真值，再报JSD/RMSE或显著性；对sc/snRNA和Visium平台差异、RNA counts深度、gene alignment要明确报告。
