# 2026-11-24 下一项：真实MERFISH第二独立来源外部验证 —— Moffitt 2018数据选择与准备（待Windows下载/检查）

## 已核实公开数据证据 [PUBLIC_SOURCE]

- Squidpy官方文档`https://squidpy.readthedocs.io/en/stable/api/squidpy.datasets.merfish.html`以及教程`https://squidpy.readthedocs.io/en/stable/notebooks/tutorials/tutorial_merfish.html`：提供Moffitt et al. 2018小鼠下丘脑视前区MERFISH真实空间单细胞预处理`AnnData`，**73,655 cells × 161 measured genes**，`obs`公开包含`Cell_ID, Animal_ID, Animal_sex, Behavior, Bregma, Centroid_X, Centroid_Y, Cell_class, Neuron_cluster_ID, batch`，`obsm`含spatial/spatial3d。教程显示下载约49.2 MB。
- 公开直链`https://ndownloader.figshare.com/files/28169379`（PIASO公共教程`https://www.piaso.org/tutorials/spatial-merfish/`列出）。原始研究Dryad `https://doi.org/10.5061/dryad.8t8s248`（Moffitt等，2018，Science，`10.1126/science.aau5324`）。
- 重要原始数据说明：Moffitt Dryad全细胞CSV记录包括原位单细胞位置、作者类别及135基因按体积标准化后的表达值，另21基因的信号为荧光单位/µm³；它们与真实raw integer RNA molecule counts不等价。当前Squidpy`h5ad`亦明确为**preprocessed**，未核实存储的`.X`是不是原始counts，**绝不可直接称为原始整数counts或为了兼容RCTD/cell2location四舍五入**。
- 该数据为完全不同研究和测量平台，相对于先前cortex-SVZ与seqFISH+是一个独立来源；而且具有动物ID，若满足各动物类别覆盖，可按**动物ID**而非spot或cell随机拆分来构造真正跨动物留出实验。
- 数据的`Cell_class`是作者标注来源而非无误差的真实物种级显微独立真值；后续由原位细胞真实坐标分箱形成spot组成可称**annotation-derived truth**，不能声称低分辨率Visium存在直接人工比例真值。
- 备选若预处理表达不满足六种counts模型要求：STARmap mouse visual cortex 1207 cells ×1020 genes，原始count+坐标+作者cell_type整合CSV公开方案见`https://iimpact.readthedocs.io/en/latest/starmap_example.html`；Zenodo镜像`https://zenodo.org/records/10698912`大小约471kB。**注意STARmap有些衍生下载只有层标签而非真实cell_type，必须确认字段和数据单位后才能当细胞类型组成真值**。

## 本轮已完成

[CODE_COMMITTED_NOT_RUN] GitHub新建[MERFISH外部来源下载与检查脚本](../external_merfish_moffitt_source_inspection.py)。它仅在用户执行时下载公开Moffitt/Squidpy H5AD至`D:\Research\STdeconv_benchmark\data\external\MERFISH_Moffitt_2018\moffitt_merfish_squidpy_preprocessed.h5ad`，复用已有文件不覆盖，流式下载/核验HDF5签名、SHA256、固定数据量、所有obs字段、动物/类别分布及空间坐标；抽样检查数值是否负值/非整数及存在`layers`/`raw`，输出`source_inspection.json`。**不会生成伪spot，不会训练任何方法，尚未在用户Windows下载或预检，当前外部验证结果为NONE**。

## 后续合理实验蓝图（方案，非实测）

1. 依据真实`Animal_ID`、`Behavior`、`Bregma`和`Cell_class`统计，选择至少一个完全没参与参考/校准的animal作为独立测试来源，严格防止同一动物细胞出现在reference/train donor和test，多个动物时按真实动物层级报告每个结果。
2. 仅在原位实验切片/动物**内部**用真实(x,y)划定固定空间bin或坐标邻域，多个细胞组成一个合成的低分辨率spot；按作者细胞类计算真实type fraction；不能把随机细胞混在任意位置称“真实空间结构”。
3. 与先前CARR reference-only seqfishplus单spot模块对齐，按真实稀有类型占比（仅train定阈值）评估rare AUPRC/positive MAE/overall JSD/matrix RMSE和zero false positive；对照Tangram/原CARR定义一致、无test真值学习。CTW若要跨来源对照，需在训练侧产生匹配方法预测再冻结CTW权重，不能仅把旧cortex-SVZ CTW权重生搬到新类别。
4. 技术限制：MERFISH为161靶向基因，且预处理值计量单位待核实，**若原数据不是count，禁止直接用counts分布假设严格的RCTD/cell2location作宣称公平的全六方法实验**；此时主比较可优先使用可接受非负表达的参考匹配算法并明确范围，或转向另一独立有真raw-count源。
5. 每个动物/切片/FOV明示层级，不把spot、seed当独立生物重复。外部实验所有负结果入库。先做小规模外部一次验证而不是再运行四次20k epoch CPU训练；GPU使用独立预检，避免既有CPU项目覆盖。
6. 按用户此前明确要求：**剩余实验证据先补，最终再集中审计**；但已经完成CTW/CARR的Methods/Results可同步起稿，不能因此推断已经达到投稿标准。

## 下一步用户单条Windows PowerShell

```powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only; if ($LASTEXITCODE -eq 0) { & "D:\ProgramData\miniconda3\envs\cell2loc_env\python.exe" "D:\Research\st-deconvolution-research\CTW-RF\experiments\external_merfish_moffitt_source_inspection.py" --download }
```

预期下载约49.2 MB并出现`DATASET 73655 cells 161 genes`、`GROUP Animal_ID unique ...`、`GROUP Cell_class unique ...`、`EXPRESSION ...`和`SOURCE INSPECTION PASS`。若服务器拒绝、网络中断或依赖错误，提供终端输出；预检失败**不启动训练**。
