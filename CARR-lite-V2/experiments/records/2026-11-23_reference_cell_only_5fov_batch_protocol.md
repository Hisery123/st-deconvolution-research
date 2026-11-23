# 2026-11-23 CARR-lite V2 reference-cell-only synthetic training → held-out seqFISH+ FOV批处理设计

## 证据与输入来源

[USER_PASTED_SOURCE] 2026-11-23研究者Windows依次提供：
- `run_carr_lite_v2_seqfishplus_5fold.py`：完整CARR 5-FOV runner，已核实训练用其它真实FOV的已知真值，**不是 reference-cell-only 合成训练**。
- `run_tangram_seqfishplus_5fold.py`：五折外层调度，`--mode cells --density_prior rna_count_based --num_epochs 500 --max_genes 3000 --seed 0`。
- `methods/Tangram/run_tangram_self_benchmark.py`：完整实际Tangram核心代码，**本次已直接阅读其输入、基因筛选、映射和输出**。读取 `pseudo_spot_expression.csv`、`sc_reference_counts.csv`、`sc_reference_labels.csv`、`pseudo_spot_locations.csv`；对齐cells/spots/genes，用sc+st表达选至多3000个基因，`tg.map_cells_to_space`模式cells，输出`predictions/Tangram_self_benchmark.csv`。**该代码不读取spot真值以拟合Tangram**，输入ST表达可无监督参与基因排序（transductive）。
- 完整Python核心文件尚未复制入GitHub研究库，实验通过本地已验证路径调用，不改变用户原版代码。

## 批处理已提交GitHub（待Windows dry-run/正式执行）

脚本：[carr_reference_only_seqfishplus_batch.py](../carr_reference_only_seqfishplus_batch.py)

- 预定义5个外层`held_out_FOV0..4`，全部使用**各自outer fold参考细胞**。参考来自seqFISH+同源单细胞定位成像数据，不应写成独立scRNA-seq测量平台或独立供体。
- 每个参考celltype内固定seed分为约40%生成池generator /60%映射参考池mapper；最低保留每类1个mapper细胞，单例类只保留mapper。严格generator与mapper cell IDs不重叠；outer fold本身已按既有脚本排除留出FOV来源细胞（此处复用，最终整体审计另行复核）。
- 默认每外层fold从generator生成`400`个6–12细胞合成spot：200个自然池按细胞均匀抽样、200个稀有富集（稀有类型由训练generator类频数的最低1/3确定），同一spot内无放回、**不同spot间允许共享generator细胞**。训练真值为生成的细胞计数比例；此训练素材与test真值无关。
- 为避免训练和测试Tangram采用不同reference配置：**分别运行训练合成spot Tangram以及留出FOV目标spot Tangram**（每FOV 2次，共10个base Tangram mappings），两者都仅使用对应同一个mapper参考细胞池，超参数`mode=cells density_prior=rna_count_based num_epochs=500 max_genes=3000`；不采用旧目录中全参考的Tangram预测作为公平对照。
- 基于用户原runner的`reference_profiles`/`build_candidates`/`fit_models`/`make_predictions`/`evaluate`复用12维特征及原始三分支HGBC超参数；`marker_k40/confusion_k3/Gate_a50`固定。测试FOV的真实`pseudo_spot_ground_truth.csv`/`..._counts.csv`**直到三种预测全部输出后才读取**，只用于最后评价。
- 结果按FOV输出新独立`D:\Research\STdeconv_benchmark\results\CARR_reference_only_seqfishplus_20261123_v1`，训练模拟表达、真值、mapping-cell参考、测试表达和预测分开。核心三分支结果`CARR_reference_only_Gate_a50`与新`Tangram_reference_matched`、`CARR_reference_only_AbundanceOnly`按5FOV比较。结果CSV `all_fov_metrics.csv`、`five_fov_descriptive_means.csv`、`paired_fov_differences.csv`。不会改旧输入/训练结果目录。
- 预检使用`--dry-run`，保证无写盘；正式需单独`--run`。脚本默认拒绝覆盖非空目录；如中断可用同参数`--run --resume`继续已有输出。错误保留子进程日志，不以外部信号推断是否成功。
- **当前只是在GitHub创建脚本，尚未用户Windows同步、预检或运行。** Python静态语法与运行成功不能靠代码存在推断。当前还没有新C3实验指标，不能编造或从原先5FOV结果转填。

## 方法与解释边界

1. 此设计**不满足真正跨平台**“独立scRNA-seq来源训练→真实组织捕获spot”泛化。它是**在同一seqFISH+细胞成像来源中，参考细胞构造训练伪spot → 留出FOV的spatially-informed pseudo-spot**，属于更接近无目标真值部署的增量检查。
2. 数据中的70个留出spot由真实空间定位单细胞按网格求和构造，**不是独立物理Visium捕获spot**；五个FOV未证明来自独立生物供体。
3. pseudo training spot复用少量generator细胞、并非400个独立训练生物单位；与旧FOV结果参考池、训练标签来源、基础Tangram预测均不同，因此**不能直接把两批的绝对均值当控制变量唯一变化归因的消融**。比较新批内部matched Tangram/CARR。
4. 不允许用test truth决定稀有类型、基因选择、超参数、早停/挑结果；本批固定超参数，保留所有5FOV和负结果。
5. 如单一FOV没有足够generator细胞或Tangram报错，保留日志，用户手动返回；脚本不自动隐藏失败。任何新结果只能来自用户Windows实际stdout/CSV。

## 下一个唯一人工动作

Windows PowerShell一条命令：先Git `pull --ff-only`，若成功则对新脚本进行`--dry-run`。成功应打印5个CHECK以及`DRY RUN PASS — no files written`；若报错直接贴输出，不启动正式批处理或修改原数据。
