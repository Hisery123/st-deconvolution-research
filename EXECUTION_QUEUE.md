## 2026-11-23 最新：CTW cell-disjoint补充实验正式运行完成，锁定结果并推进DLPFC批应用

- [USER_WINDOWS_RUN] `ctw_cell_disjoint_reference_batch.py --run`：836 cells、10000 genes、19 types，reference419/train donor204/test donor213，5类L12/L16/L17/L4/L8在train/test无成员。balanced与cell_uniform各重跑Tangram train/test（四次映射均DONE），16 method-scenario评测行全成功，SoftOpt fallback 0，结果`D:\Research\STdeconv_benchmark\results\CTWRF_cell_disjoint_20261123_v1`。[全部原始终端表与负结果](CTW-RF/experiments/records/2026-11-23_cell_disjoint_3baseline_full_run_completed.md)。
- [BALANCED] SoftOpt JSD .254912/matrixRMSE .083280/aggRMSE 1.348836；GlobalStacking .263915/.084946/1.420992；**InvRMSE_p2 JSD .249645 优于SoftOpt**，应保留反例。
- [NATURAL] SoftOpt JSD .143227/matrixRMSE .062353/aggRMSE .959604；Global .146024/.062554/.966025；Tangram JSD .144009，SoftOpt优势仅0.000782，避免夸大。
- [LIMITATION] 新实验只重新运行Tangram/NNLS_500/NNLS_marker20三个基础方法，**不是旧6法全部去重叠重跑**；来源细胞组互斥，但均同一cortex-SVZ样本/域，不能称独立生物学复现。伪spot内部及组内可重复抽细胞。
- [USER_WORKFLOW] 先完成实验再集中审计，不在本批测试上重复调参或做碎片审查。下一批转向**CTW DLPFC 12切片应用**，优先找已存在的`D:\Research\real_DLPFC`和`D:\paper\ST_Benchmark_Planning\mvp\data`里可复用的输入及脚本，再创建一键批处理；尽量把检查集成dry-run，用户Windows一次一个短步骤。无真实组成真值的切片不计算反卷积RMSE/JSD。

## 2026-11-23 下一批已写好：CTW-RF细胞ID三组隔离的补充3基线实验（未运行）

- [USER_DIRECTIVE] 先跑完实验再系统审计。按此要求直接编写并提交[CTW reference-cell-disjoint补充batch](CTW-RF/experiments/ctw_cell_disjoint_reference_batch.py)和[冻结协议](CTW-RF/experiments/records/2026-11-23_cell_disjoint_3baseline_supplementary_batch_protocol.md)，**Windows还未同步/预检/运行，绝对没有此批新指标**。
- [PROTOCOL] 从`data\groundtruth\self_benchmark_cortex_svz`原始single-cell引用按类别拆成互不交叉的mapper reference/train donor/test donor；balanced_celltype与cell_uniform两个场景，每场景1200个train+800个test合成8细胞spot；用同一reference重新训练Tangram（专用Conda Python3.7，500epochs/3000genes，每场景train/test分别拟合）和参考式NNLS_500/NNLS_marker20；训练折真值训练GlobalStacking/CTW_SoftOpt/HardSelect/InvRMSE，独立来源细胞的test spot上评估，共3基础+5融合=8方法×2场景16行。测试cell IDs与reference及训练伪spot donor互斥，组内spot重复使用细胞，非独立生物重复。
- [LIMITATION] 此实验**不等于旧六种反卷积基础法的完全无交叉重跑**，因为研究仓库没有保存其余5法完整run入口。旧6法重跑和新平台外部验证仍留队列；不能拿旧预测与新无交叉参考混合比较或声称已经解决全6法问题。
- [NEXT SINGLE ACTION] Windows用一条PowerShell拉GitHub后立即执行`ctw_cell_disjoint_reference_batch.py --dry-run`，检查Tangram导入、数据拆分、两种采样内存冒烟与NNLS，不写盘；通过后下一轮再单条`--run`批量运行四次Tangram和所有对照。若报错保留日志。
## 2026-11-23 用户最新强制执行偏好：停止反复审核，先把补实验跑完

- [USER_DIRECTIVE] 用户明确说“别在一个劲的去审核1这个1审核那个的，咱们按计划进行，最后再审核”。**立即停止独立重复的来源审计、泄漏审计、零碎表头检查和论文质量评审**，除非缺失会直接阻止一个即将执行的实验；即使确需检查，也尽量嵌进一个批处理`--dry-run`，不要让用户手工反复发多条输出。先完成剩余实验，之后用户交Claude统一审计。
- [USER_PASTED_REVIEW] 用户同时附先前Claude建议：CARR跨RCTD/CARD、严格类别留出、去深度、简单校准/特征消融、参考合成训练、MERFISH/STARmap外部数据；CTW EnDecon/stacking、参考细胞与伪spot细胞隔离重跑、DLPFC多切片和独立数据、统计、写作。把其作为任务清单，不把该长文本视作已执行的现状或新证据。
- [ALREADY_COMPLETED] CARR RCTD/CARD跨方法+严格类别留出+no_depth+简单校准/敏感性共12批和有关52视图，以及同源seqFISH+ reference-only 5FOV全部完成；CTW GlobalStacking36、同折5fold×3seed×3pool的9项、EnDecon聚合3池已完成。不得因Claude旧建议重新跑已完成工作。
- [REMAINING_PRIORITY] ① CTW旧2000spots基准reference来源细胞与generator不隔离，**需要真正做去重叠参考拆分的新版实验**，不是再静态审计旧代码；② CTW 12张DLPFC若本地已有必要输入则批量外部定性应用；③ CARR/CTW不同数据来源的外部应用或有真值数据实验（本地Visium有sc及ST四文件，但暂无真实组成真值；MERFISH现有文件名为simMERFISH计数及坐标，是否含真值未知）。统计检验、系统论文审计、投稿评估后置。
- [NEXT STYLE] 下一轮直接选定可执行的新实验、写GitHub batch runner、用户本地仅一条`git pull + --dry-run`及一条后续`--run`；失败才精确排障。不再让用户为已有数据连续做表头/来源/ID核验。

## 2026-11-23 最新：Visium四份CSV已读两行，mouse-brain外部应用候选（完整对齐待核）

- [USER_WINDOWS_READONLY] `data\visium\sc_mousebrain.csv` 2081.93MB：cell×12819genes、第一列5705STDY8058285_...；`sc_celltype.csv` 1.77MB标注`annotation_1`首例Astro_AMY；`st_count.csv` 161.12MB：gene×2576spots（需要转置）；`st_location.csv`约0.07MB列为spot ID、row、col。共享基因前两行可见Xkr4/Gm1992，但**完整集合、spot对齐和真值尚未验证**。[逐文件证据与外部来源线索](CARR-lite-V2/experiments/records/2026-11-23_visium_external_dataset_schema_first_read.md)。
- [EXTERNAL_SOURCE_HYPOTHESIS] cell2location官方小鼠脑教程使用相邻切片snRNAseq/Visium，BayraktarLab Github discussion列有5705STDY8058285样本；因此本地sc ID与公开cell2location数据存在强线索，但**本地Visium空间数据对应哪张具体切片尚不能据此断定**。
- [NEXT SINGLE ACTION] Windows只读、内存友好检查：仅读取sc_mousebrain的表头（2GB矩阵不全载）、st_count的第一列和表头、坐标文件和细胞标签文件；报告gene交集、spot/coords匹配、重复ID、标签类别数。进一步设计跨平台外部应用前先确认定量真值是否存在，不能用模型输出当真值。
## 2026-11-23 最新：MERFISH/Visium文件名核查，优先Visium外部应用候选

- [USER_WINDOWS_DIRECTORY_FILES] 在`D:\Research\STdeconv_benchmark\data\MERFISH`只见`simMERFISH_20_st_count.csv`, `simMERFISH_50_st_count.csv`, `simMERFISH_100_st_count.csv`及各自st_location.csv（递归Depth2，前30项）。文件名`sim`提示模拟性质；尚未核实构造来源、细胞真值或单细胞参考，不能断言具备外部定量真值。
- [USER_WINDOWS_DIRECTORY_FILES] `D:\Research\STdeconv_benchmark\data\visium`存在`sc_celltype.csv`、`sc_mousebrain.csv`、`st_count.csv`、`st_location.csv`，另有`__MACOSX`伴生文件（可忽略）。这只是参考、标注、ST表达、坐标四类文件名，**原始数据来源、平台真实性、基因/ID配对、类型比例真值及统计独立性仍未验证**。
- [PRIORITY] 用户要先完成实验再综合审计；优先查看visium四CSV的文件大小、表头列数、各首两行的ID与字段，严格只读、避免全量载入超大矩阵。若无目标组成真值，后续仅外部部署/定性或已定义的代理一致性验证，不能以假真值计算MatrixRMSE/JSD。
- [NEXT SINGLE ACTION] Windows单条PowerShell调用当前python对visium四文件`pd.read_csv(nrows=2)`，报告文件大小、表头数量与前几列/行，判断表方向后再设计数据集适配。
- [LOCKED] CARR同源reference-only五FOV真实结果已完成及配对锁定，Gate a50 AUPRC 5/5提高、MatrixRMSE 5/5提高、JSD 4/5提高、SingletonRMSE仅2/5提高；不在同源测试FOV追加后验调参。

## 2026-11-23 最新：本机data一级目录已有MERFISH、seqFISH+、seqFISH_PLUS_CaiGroup和visium候选

- [USER_WINDOWS_DIRECTORY_LIST] 用户一条只读PowerShell命令列出`D:\Research\STdeconv_benchmark\data`现有五个一级子目录：`groundtruth`、`MERFISH`、`seqFISH+`、`seqFISH_PLUS_CaiGroup`、`visium`。不同目录名不证明不同独立供体/实验来源，亦未核实原始真值。
- [PRIORITY] 后续优先检查MERFISH（可能有单细胞表达/注释/坐标以形成新的空间聚合伪spots，仍非物理测量spot）与visium（可能有真实捕获spots，但真实celltype组成不一定可得）。未检查任何文件内容前不能声称有独立的定量真值或模型已经能运行。
- [NEXT SINGLE ACTION] Windows PowerShell一条只读命令枚举MERFISH和visium各前若干文件的路径，限制递归深度和输出条数，确定数据源、文件格式、同源关系、原始真实细胞比例真值可能性。不得创建、转换或重跑任何文件。
- [PROGRESS] 刚完成CARR参考细胞训练五FOV逐折真实核查；Gate a50 AUPRC 5/5、matrixRMSE 5/5、JSD 4/5、singletonRMSE 2/5，指标已归档锁定，不对测试FOV后验调参。

## 2026-11-23 最新：groundtruth现有七目录均尚不能确认独立外部来源，优先盘点data其它目录

- [USER_WINDOWS_DIRECTORY_LIST] 用户在Windows只读列出`D:\Research\STdeconv_benchmark\data\groundtruth`七文件夹：`rarecell_52scenario_suite`、`self_benchmark_cortex_svz`、`self_benchmark_cortex_svz_2000spots`、`seqfishplus_cortex_real_spatial_noleak`、`seqfishplus_cortex_svz_author_rect`、`seqfishplus_cortex_svz_fov_bins500`、`seqfishplus_rarecell_noleak_v1`。**目前是目录名证据，不等于全七个已逐个核查原始细胞ID和测序来源**。
- [TRIAGE] 52scenario和2000spots为已充分研究的衍生伪spot；刚完成5FOV seqFISH+同源reference-only；其余名为seqfishplus的目录很可能同域或加工变体，外部独立性未证实，不能充作新增独立供体/跨平台验证。
- [NEXT SINGLE ACTION] Windows只读列出`D:\Research\STdeconv_benchmark\data`一级子目录，检查外部DLPFC/MERFISH等候选是否现存；如果存在再看文件结构/独立真值情况。无需重跑已完成五折、CTW同折或EnDecon批次。
- [LOCKED_CARR] reference-only 5FOV Gate a50 AUPRC 5/5、matrixRMSE 5/5、JSD 4/5、singletonRMSE仅2/5；不在同一数据上后验调门控参数。审计最后由Claude整体进行。

## 2026-11-23 最新：CARR reference-only 5FOV完整逐折结果+全部负指标已经核对

- [USER_WINDOWS_CSV_SUMMARY] 用户贴出`all_fov_metrics.csv`15行、`paired_fov_differences.csv`10行，已逐项转录为[五FOV全部配对证据记录](CARR-lite-V2/experiments/records/2026-11-23_reference_only_seqfishplus_all_fov_paired_confirmed.md)。不是助手实际读取本地CSV字节。
- [RESULT] Gate_a50对同一reference匹配的Tangram：singleton-vs-zero AUPRC **5/5 FOV改善**、matrixRMSE **5/5改善**、mean_spot JSD **4/5改善**（FOV0 +0.000109微幅恶化）、singleton RMSE **2/5改善**（FOV0 +.003153、FOV2 +.000895、FOV4 +.004211恶化）。
- [SIMPLE_BASELINE] AbundanceOnly同样有JSD **5/5改善**、matrixRMSE **5/5改善**、singleton AUPRC **5/5改善**，singleton RMSE仅2/5改善；Gate a50的JSD仅FOV1优于AbundanceOnly，在其余4个FOV更差；门控分支不能被称为全部增益的必要原因。
- [METHOD_BOUNDARY] 5FOV不等于5独立供体；70spots是位置引导细胞聚合而非物理测得spot；singleton_vs_zero_AUPRC不等价所有rare-positive检测；参考训练来自同源seqFISH+单细胞，不是独立scRNA测序平台。不得就相关FOV直接做独立生物重复显著性宣称或挑选性报结果。
- [NEXT] 用户要求先完成剩余研究实验、Claude最终集中方法/论文审计；**当前reference-only FOV结果固定，不再此数据集反复尝试调参**。下一步应盘点可用于真正外部验证的现存独立数据（有实际参考、组成真值和跨类型基因支持时才能定量验证），或CTW真实切片定性泛化，不能臆造数据/实验结果。无需重新跑已完成的CARR12、CTW36/9、EnDecon和本批5FOV。

## 2026-11-23 最新：CARR reference-cell-only 5FOV整批全部成功，性能增益有限且有负指标

- [USER_WINDOWS_RUN_LOG] 使用Tangram专用Python3.7 CPU环境、CARR主Python3.10完成`carr_reference_only_seqfishplus_batch.py --run --resume`；终端`BATCH FINISHED 5 FOV; 15 held-out method/FOV metric rows`，结果位于`D:\Research\STdeconv_benchmark\results\CARR_reference_only_seqfishplus_20261123_v1`。[真实汇总和FOV2–4日志](CARR-lite-V2/experiments/records/2026-11-23_reference_only_seqfishplus_batch_complete.md)。
- [RESULT] 5FOV等权均值 Tangram_reference_matched JSD .431365/matrixRMSE .099243/singleton_RMSE .131094/singleton_vs_zero_AUPRC .227871/AUROC .644309；CARR_reference_only_Gate_a50 分别 .423617/.097243/**.132314（恶化）**/.261662/.668072；AbundanceOnly .422088/.097947/.131216/.259739/.667002。零位点预测均值Tangram .035435、Gate .035628（略恶化）、AbundanceOnly .035054。Gate JSD改善约1.8%，AUPRC相对提升约14.8%，但比AbundanceOnly JSD稍差。需要保持所有负结果和对照公平性解释。
- [PENDING_READ] FOV2/3/4 Gate JSD和AUPRC改善，**FOV0和FOV1逐折原始CSV尚未读取**；不能声称5/5 FOV全部方向一致。下一步单条Windows只读命令读取`all_fov_metrics.csv`和`paired_fov_differences.csv`，确认逐折负结果和方向计数。
- [BOUNDARY] 本次参考细胞来自seqFISH+相同数据来源，测试70spots为spatially-informed pseudo-spots，非独立真实捕获spot；5FOV不等于5独立供体，400合成训练spots也非独立生物样本；与旧五FOV使用其它FOV目标真值训练的实验存在参考拆分及Tangram重训练等多处变量差异，不用旧绝对均值作唯一因素因果推断。
- [WORKFLOW] 初次因`.venv`缺tangram失败，修复专用解释器后成功；保留此前失败日志。用户仍计划先补完实验后交Claude集中审计；后续优先新外部验证及独立来源，不重新跑CTW36/9及CARR12已完成批次。

## 2026-11-23 最新：CARR reference-only新实验首次FOV0因Tangram导入失败中断，独立解释器/恢复补丁已提交

- [USER_WINDOWS_ERROR] 初次`--run`在`START FOV 0`后，Tangram子进程导入阶段报`ModuleNotFoundError: No module named 'tangram'`。实际子进程错误使用`D:\paper\ST_Benchmark_Planning\mvp\.venv\Scripts\python.exe`，非Tangram专用环境。尚未完成任何映射训练或5FOV评价；保留已生成的FOV0合成spot数据和`run_config.json`。
- [USER_WINDOWS_CHECK] 用户在Windows明确运行`D:\ProgramData\miniconda3\envs\Tangram\python.exe`并得到`Tangram import PASS; CUDA: False`，可以单独用于Tangram子进程，但该环境当前看起来只运行CPU（不保证GPU）。[失败记录与修复](CARR-lite-V2/experiments/records/2026-11-23_reference_only_first_run_python_environment_failure.md)。
- [CODE_COMMITTED_NOT_USED] 对[CARR批处理脚本](CARR-lite-V2/experiments/carr_reference_only_seqfishplus_batch.py)增加`--tangram-python`，将CARR主环境与Tangram子解释器分离；允许`--dry-run --resume`对现有run_config检查解释器依赖，`--run --resume`时单独记`tangram_python_runtime.json`以保护既有run_config、拒绝未知环境混用。修复提交已在GitHub，**尚未在Windows同步/运行修复版**，不宣布修好或完成结果。
- [NEXT SINGLE ACTION] Windows一条PowerShell先Git pull成功后执行`--dry-run --resume --tangram-python "D:\ProgramData\miniconda3\envs\Tangram\python.exe"`；若成功下一轮再`--run --resume`，不删除目录或重跑旧已完成实验。
- [SCIENCE] 既有5 FOV/70 spots源于同源seqFISH+空间单细胞重构，非独立生物学重复；本次实验状态FAIL/REPAIR_PENDING，无可用新性能结果。

## 2026-11-23 最新：CARR五FOV reference-cell-only训练批处理已创建GitHub，等待Windows预检

- [USER_PASTED_SOURCE] 用户提供`D:\Research\STdeconv_benchmark\methods\Tangram\run_tangram_self_benchmark.py`完整源码，确认Tangram的实际4文件输入及`map_cells_to_space`调用、3000基因选择和现有预测输出接口。见[新方案说明](CARR-lite-V2/experiments/records/2026-11-23_reference_cell_only_5fov_batch_protocol.md)。
- [CODE_COMMITTED_NOT_RUN] 新建[CARR参考细胞合成训练→留出seqFISH+五FOV批处理](CARR-lite-V2/experiments/carr_reference_only_seqfishplus_batch.py)：每outer fold参考细胞按类拆成generator与mapping细胞不重叠，固定400个6–12细胞训练伪spots（自然/稀有富集各50%），用相同mapper分别对训练伪spot与留出目标FOV重跑Tangram（总计划10次Tangram映射），用原CARR三分支12特征+HGBC固定marker40/confusion3/Gate_a50训练和推理。测试FOV真值仅在三种预测输出后用于评价；每FOV单独日志和结果，非空输出目录禁止覆盖，可--resume。
- [SCIENTIFIC_BOUNDARY] 这里的“reference-only”不等同独立scRNA测序平台，因为参考细胞仍来自seqFISH+来源；测试70spot仍为按真实空间单细胞网格汇聚的pseudo spots，不是物理捕获spot；5 FOV不等于5独立供体。原始旧CARR FOV基线参考设置与新matched Tangram不完全相同，不直接用旧baseline效应比较归因。训练400伪spots复用generator细胞，是合成增强并非独立样本。
- [STATE] 新批脚本仅提交GitHub，**Windows尚未git pull/--dry-run/--run；没有任何新CARR reference-only真实数据泛化实验结果**。不推断新实验改善，静态语法也需通过用户预检确认。
- [NEXT SINGLE ACTION] Windows一条PowerShell先`git pull --ff-only`，拉取成功则执行`python ...\CARR-lite-V2\experiments\carr_reference_only_seqfishplus_batch.py --dry-run`。通过后再单条`--run`批量完成5折；失败贴原始日志，保护已有CARR/CTW结果。
- [WORKFLOW] 用户已决定批量做完计划实验，最后由Claude集中全面审计；当前保留必要数据/标签边界和失败记录。

## 2026-11-23 最新：已收到完整seqFISH+ CARR五FOV runner，reference-only训练仍缺Tangram生成接口

- [USER_PASTED_SOURCE] 用户已上传本地`run_carr_lite_v2_seqfishplus_5fold.py`完整`Get-Content -Raw`结果；在助手容器提取shebang至if-main并`compile()`语法检查PASS。完整来源与C3实施方案见[源码阅读与下一批实验计划](CARR-lite-V2/experiments/records/2026-11-23_seqfishplus_runner_source_received_deployment_plan.md)。
- [METHOD_FINDING] 原runner的外层FOV留出，是**从其它FOV已知目标组成标签构造训练候选**，不是原计划C3的reference-only单细胞模拟伪spots训练。必须另造训练伪spot并为它生成同协议基础Tangram预测后才能训练CARR。原runner读取现成`predictions/Tangram_self_benchmark.csv`，不包含Tangram计算代码；不可用理想预测+加噪/NNLS代替并宣称同基线公平。
- [NEXT SINGLE ACTION] Windows一条只读PowerShell`Get-Content -LiteralPath "D:\Research\STdeconv_benchmark\run_tangram_seqfishplus_5fold.py" -Raw`取得当前Tangram生成代码，再一次性编排5个holdout FOV的模拟spot参考训练和测试。**尚未提交/运行reference-only新实验**；旧FOV批结果不要覆盖、旧模拟CTW/CARR不重跑。
- [BOUNDARY] 参考细胞来自seqFISH+同域已有数据，不等于独立外部scRNA-seq平台；5FOV/70人工聚合spots不是5独立供体/70生物学样本。用户决定最终Claude集中审计，现阶段维持输入/标签隔离后优先实验。
## 2026-11-23 最新：EnDecon聚合核心权重与三种简单对照已从Windows CSV读取，准备CARR真实FOV下一批实验

- [USER_WINDOWS_CSV_SUMMARY] EnDecon聚合移植的`endecon_weights_by_pool.csv`、`ensemble_metrics_by_pool.csv`、`endecon_diagnostics_by_pool.csv`由用户Windows命令读出。详见[完整权重、指标和诊断记录](CTW-RF/experiments/records/2026-11-23_endecon_weights_aggregation_console_results.md)。
- [FINDING] strong2的cell2location权重为**0.880797**（CARD仅0.119203），二基线加权中位数直接输出cell2location预测，JSD **0.098996**、RMSE **0.056752**；**这不是带来额外改善的新融合**。expanded4 CARD权重0.480304、cell2location 0.287698；full6方法权重均较分散、最大RCTD0.228215。
- [REAL_NEGATIVE] full6的EnDecon移植版JSD **0.233707**、RMSE **0.073754**，不如普通坐标中位数**0.216576/0.070923**，也不如等权均值**0.160047/0.058340**；这说明该实现对当前基础池可能很敏感，但具体原因未经逐celltype复核，不可作为算法普遍劣势。三个pool均3轮收敛（lambda347.666/1120.918/1384.483）；移植版聚合运行仅0.0078–0.0229秒、不含基线训练。
- [METHOD_BOUNDARY] CTW SoftOpt与EnDecon存在监督信息不对称：CTW使用fold训练真值，EnDecon使用全体spot预测无监督聚合；本次并未运行EnDecon作者完整R管线。用户另行贴出`E4_GITHUB_URL`指向`Hisery123/st-clustering-research`，这是不同项目，不要混为本研究数据。
- [NEXT SINGLE ACTION] 为继续用户指定**CARR scRNA-only参考构建伪spot训练→留出seqFISH+ FOV验证**路线，需要先读取用户Windows本地尚未归档的`D:\Research\STdeconv_benchmark\run_carr_lite_v2_seqfishplus_5fold.py`当前源码（单条只读PowerShell）；拿到之后直接准备可批处理脚本，避免再做模拟参数扫与反复全面审计。

## 2026-11-23 当前下一步：读EnDecon权重、无监督简单对照指标，然后推进新数据批实验

- [USER_WINDOWS_STDOUT] EnDecon**Python聚合核心移植版**3池运行结束：strong2 JSD .098996, RMSE .056752；expanded4 .119340/.051988；full6 .233707/.073754，各3轮收敛，调度器声明共9个变体结果、18个CTW参照比较。[原始日志](CTW-RF/experiments/records/2026-11-23_endecon_aggregation_run_results.md)。
- [FINDING] strong2池EnDecon JSD好于CTW SoftOpt（CTW三seed均值.114850），但CTW RMSE好于EnDecon（.052449 vs .056752）；expanded4/full6池CTW两个指标都好。不得过滤或隐瞒strong2这个反例，也不能把seed视作独立外部样本。
- [NEXT SINGLE ACTION] Windows一条只读命令打印`endecon_weights_by_pool.csv`、`ensemble_metrics_by_pool.csv`、`endecon_diagnostics_by_pool.csv`；仅在得到真实权重后分析强2池退化/全6池恶化原因。
- [AFTER] 优先CARR参考scRNA-only训练→留出FOV真实目标，和CTW DLPFC/新外部真实数据上的泛化；批量脚本、严守数据边界；全面论文/泄漏审计在实验完成后交Claude。
## 2026-11-22 当前唯一下一实验：EnDecon论文算法近邻对照（聚合核心移植），先同步预检

- [USER_RESULT] CTW同折3seed×3pool最新原始控制台输出：full6 SoftOpt JSD .101723、matrixRMSE .041453、aggregateRMSE .725489，对Global .113531/.048966/.867231；9/9 JSD+RMSE改善Global、HardSelect；对InvRMSE_p2与EqualWeight JSD仅6/9改善。fit mean SoftOpt .331s vs Global .015s。详见[实际CSV摘要归档](CTW-RF/experiments/records/2026-11-22_ctw_matched_fusion_metrics_from_user_console.md)。
- [GITHUB_CODE_READY_NOT_RUN] 论文EnDecon（Tu et al. 2023, DOI 10.1093/bioinformatics/btac825）作者R`solve_ensemble()`已直接核对核心；新建[3方法池批处理](CTW-RF/experiments/ctw_endecon_aggregation_batch.py)，仅融合已有2/4/6预测与CTW matched fold结果对照，不声称完整R包复现。[协议](CTW-RF/experiments/records/2026-11-22_endecon_aggregation_extension_protocol.md)。
- [NEXT SINGLE ACTION] Windows合并GitHub pull并（仅成功时）执行新`ctw_endecon_aggregation_batch.py --dry-run`，再独立下一条`--run`。旧数据与结果目录保护；先按用户要求批量补实验，最终审计交Claude。
- [FUTURE] CARR参考scRNA训练→目标留出FOV应用、第二平台及CTW DLPFC数据验证均未完成，不提前填结果。

## 2026-11-22 最新：CTW主方法同折9/9成功，下一步读取三CSV

- [RUN_LOG_CONFIRMED] CTW 2000spot/19类/6方法同折5fold：3seed×3pool共9配置全部完成、81方法级摘要；SoftOpt的JSD在9/9配置优于GlobalStacking，optimizer fallback为0；full6在3种seed上的SoftOpt JSD 0.101752/0.101690/0.101727，global JSD 0.113543/0.113507/0.113544。[运行记录](CTW-RF/experiments/records/2026-11-22_ctw_matched_fusion_9_seed_pool_completed.md)。
- [PENDING_READ] 新CSV中的matrix_RMSE、aggregated_celltype_RMSE、完整配对差与fit_runtime尚未读取；不能仅凭JSD宣称所有指标占优。
- [NEXT SINGLE ACTION] Windows一条Python只读命令汇总`summary_metrics_by_seed_pool.csv`、`paired_differences_by_seed_pool.csv`、`fit_runtime_by_fold.csv`，形成完整对照判断。后续按原实验清单安排EnDecon和真实数据扩展；不再分散逐项审计，最终由Claude复核。
- [COMPLETED EARLIER] CARR12个参数/对照任务全部success，CTW GlobalStacking36配置全部完成，不应再次耗时重跑。

## 2026-11-22 最新：已获得两批真实数值，新CTW主方法同折9配置脚本待运行

- [USER_LOG_CONFIRMED] CARR12任务`batch_run_status.csv`全部`success`，包括marker20/80、confusion1/5、no_depth、LogisticPresence12/Threshold1D；CTW GlobalStacking 36/36配置的全部三seed summary已由用户命令打印。[指标归档](CARR-lite-V2/experiments/records/2026-11-22_batched_carr_ctw_actual_console_results.md)，不能将这些相关模拟视图/seed视为独立生物重复。
- [FINDING] CARR marker20相对marker40在RCTD/CARD均有描述性RMSE/AUPRC改善；no_depth近似标准配置；CARD Threshold1D检测表现不弱但定量明显变差。CTW GlobalStacking full6/all比expanded4/all RMSE低但JSD略高，缺CTW主方法同折多seed比较。
- [GITHUB_CODE_READY] [CTW主方法同折批处理](CTW-RF/experiments/ctw_matched_fusion_comparisons_batch.py)，同一2000spot基准、3 seed×3方法池、对照CTW_SoftOpt(历史Proposed_CV固定实现)、InvRMSE_p2/HardSelect/GlobalStacking/等权/单方法，记录真实逐折差异和拟合时间。不执行新数据审计或改旧输入。**此脚本在Windows尚未运行/预检**。
- [NEXT SINGLE ACTION] 用户Windows合并`git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only`和成功后`python ...\CTW-RF\experiments\ctw_matched_fusion_comparisons_batch.py --dry-run`为一条PowerShell语句，成功后另给`--run`。用户想缩短操作循环，已有原批结果绝不重新训练。
- [AFTER] CTW同折比较后再以批处理安排剩余关键实验：CTW最近邻集成方法原文可复现对照、CARR参考scRNA单独合成训练→留出FOV应用、可获取的第二平台。最终方法/数据泄漏/论文字句审计集中交Claude。
## 2026-11-22 最新：已完成CARR 12任务+CTW36配置，转向统一输出读取与下一批设计

- [RUN_LOG_CONFIRMED] CARR 12项：`BATCH FINISHED 12 jobs`；CTW 36组：`BATCH FINISHED 36 of 36 configurations; FAILED 0`。详见[CARR完成记录](CARR-lite-V2/experiments/records/2026-11-22_pending_12job_batch_completed.md)、[CTW完成记录](CTW-RF/experiments/records/2026-11-22_ctw_36configuration_batch_completed.md)。
- [NOT YET READ] CARR新`batch_run_status.csv`/`batch_metric_means.csv`及CTW`metrics_by_seed_pool_budget.csv`原始行未直接读出；不得推断新的最优参数/显著性。
- [NEXT SINGLE ACTION] 用户Windows一条只读Python命令同时打印CARR 12任务状态与selected HGBC_a30/Logistic/Threshold指标，以及CTW GlobalStacking各方法池和校准预算3-seed均值/最小/最大；然后按结果安排后续补充实验（EnDecon及Proposed同折/DLPFC应用、CARR第二平台/参考训练部署等），不要重跑原任务、不插入全面审计。
- [USER_DECISION] 写多任务批处理减少本地人工步骤；最终科学审计交Claude。所有新实验需要可复用脚本+日志、区分计划和完成。

## 2026-11-22 最新：CARR12项已运行完成；立即开始CTW36项预检

- [RUN_LOG_CONFIRMED] CARR `carr_pending_experiments_batch.py --run` 终端最终`BATCH FINISHED 12 jobs`，最后 `logistic_threshold CARD`完成156行；保存`batch_metric_means.csv`、`batch_run_status.csv`本地路径。此前12项均NEW且dry-run PASS。[完整运行末尾记录](CARR-lite-V2/experiments/records/2026-11-22_pending_12job_batch_completed.md)。
- [NOT YET ANALYZED] 用户尚未提供新CSV指标均值；不要宣称CARR敏感性最优参数/提升。预计2912结果行为按协议计算而非终端实际汇总。
- [NEXT SINGLE ACTION] 用户Windows运行CTW `python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_stacking_sensitivity_batch.py" --dry-run`。出现`DRY RUN PASS`后下一轮给`--run`一键36配置。严格不重跑此前CARR12任务，不插入项目全面审计。
- [LATER] CTW完成后用一条只读Python命令汇总`batch_metric_means.csv`、`batch_run_status.csv`并读取CTW36配置真实指标，按原计划补独立真实场景和最近邻文献对照，最终审计交给Claude。

## 2026-11-22 最新执行优先级：一次写多任务、集中跑补实验、审计终期由Claude接手

- [USER_DIRECTIVE] 不再逐轮查泄漏/生成细节；优先做原两篇扩充实验，实验结束后Claude统一审查。Windows由用户手动执行，但GPT预先写好批处理，一次人工启动多实验并保留每个子任务日志。
- [GITHUB_CODE_READY_NOT_RUN] CARR：`CARR-lite-V2/experiments/carr_pending_experiments_batch.py` 统一执行12任务：RCTD/CARD × (marker_k20、marker_k80、confusion_k1、confusion_k5、严格类别留出no_depth、固定LogisticPresence12/Threshold1D)。覆盖Claude原计划#5/#6/#7部分缺口，子任务独立、失败保护、自动汇总结果与耗时。
- [GITHUB_CODE_READY_NOT_RUN] CTW：`CTW-RF/experiments/ctw_stacking_sensitivity_batch.py` 执行36组全局stacking鲁棒性配置（3种seed×3方法池×4训练样本量），前置只读检验、结果输出隔离；不是 CTW Proposed_CV 的同折新对照。
- [PROTOCOL] [批处理实验方案与预期](CARR-lite-V2/experiments/records/2026-11-22_batched_extension_protocol.md)。已有CARR 52视图/原始严格类别留出结果、原Ridge/Isotonic和已有10组消融均不重新跑。
- [NEXT SINGLE ACTION] Windows同步远端GitHub：`git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only`。用户回传后第一条执行命令为CARR `--dry-run`，通过再`--run` 一次跑12任务。CTW随后再跑。**没有任何本批真实实验日志，不能填结果**。

## 2026-11-22 最新：seqFISH+ builder第81–265行已审查，下一步补源头及fold导出代码

- [USER_PASTED_SOURCE] `build_seqfishplus_real_spatial_noleak.py`: 第155行对按空间X/Y、FOV网格分配的目标cell表达求和；156–159行按cell_type单独算26类真值；第233–241行参考排除被留出整个FOV并断言参考/目标成员cell UID不重叠。
- [RISK AUDIT] 源`counts`是否raw、10k基因怎样选尚未见第1–80行；fold中reference导出尚未见266+；`all_cell_types`词表在全meta构建（是否发生目标标签信息暴露需核实），`reference_meta`非held-out FOV但未在该片段按Region限于Cortex；最关键runner如何用`pseudo_spot_ground_truth.csv`仍待审。不能将安全的逐spot汇总误判为必然泄漏，也不能宣称整个流水线no-leak。
- [RECORD] [2026-11-22 第81–265源码审计](CARR-lite-V2/experiments/records/2026-11-22_seqfishplus_build_spots_source_audit_lines81_265.md)。
- [NEXT SINGLE STEP] 用户PowerShell只读打印`build_seqfishplus_real_spatial_noleak.py`第1–80与266–340行（记录末尾完整命令），回传源码，再判断基因选择和fold参考输出。仍未训练/修改任何数据。

## 2026-11-22 最新：seqFISH+表达生成脚本已定位，下一步源码只读检查

- [USER_WINDOWS_STDOUT] 本机grep返回 `D:\Research\STdeconv_benchmark\build_seqfishplus_real_spatial_noleak.py` 第218行写出总表达，第257行涉及fold表达；`run_carr_lite_v2_seqfishplus_5fold.py` 第112行读取fold表达。详情 [源码定位](CARR-lite-V2/experiments/records/2026-11-22_seqfishplus_expression_builder_source_locations.md)。
- [NEXT SINGLE STEP] 用户Windows一条PowerShell命令只读打印 `build_seqfishplus_real_spatial_noleak.py` 第81–265行并附行号，核查构建、特征选择及外层fold边界。需用户回传源码内容才可下结论，不能推断源码已经审过或实验无泄漏。
- 不跑构建程序、不修改70×10000表达CSV，不补空间预测点图。

## 2026-11-22 最新：seqFISH+ 伪spot表达基础完整性PASS；下一步源码溯源

- [USER_WINDOWS_STDOUT] `pseudo_spot_expression.csv` (70×10001)：70个spot与26类真值spot_id集合唯一且相同；10,000数值表达列无NaN/Inf、负值或全零spot行。[完整记录](CARR-lite-V2/experiments/records/2026-11-22_seqfishplus_expression_integrity_check.md)。
- [LIMITATION] 这是表级完整性检查，**尚不知道**10k基因选取、成员细胞RNA汇总/归一化流程及训练/测试FOV信息边界，不能据此宣称完全无数据泄漏。
- [NEXT SINGLE STEP] 用户Windows仅在`D:\Research\STdeconv_benchmark`中用`Get-ChildItem ... *.py | Select-String -SimpleMatch "pseudo_spot_expression.csv"`定位Python生成或读取源码（记录末尾完整可复制命令）。若无结果再查其它源目录，不猜代码文件。
- 不重训练、不画空间预测图。

## 2026-11-22 最新：seqFISH+ 26类伪spot真值按514 cell-membership重建 PASS

- [USER_WINDOWS_STDOUT] metadata/membership/spots行数913/514/70；三个cell UID检查True；三个spot集合/唯一性检查True；`SPOT SIZE CHECK 70 of 70 mismatched 0`；`GROUND TRUTH MAX ABS ERROR 8.326672684688674e-17 MISMATCHED SPOTS 0`。
- [CONCLUSION] 70个有真实空间来源的pseudo-spots，其26类ground_truth可以由514条cell-to-spot membership准确重建；这不等于证明表达聚合和模型全链路无泄漏，也不等于独立真实捕获的spot。399个metadata cell未进入membership的原因尚未核对。
- [RECORD] [2026-11-22 membership与真值审计](CARR-lite-V2/experiments/records/2026-11-22_seqfishplus_membership_truth_integrity_check.md)。
- [NEXT SINGLE STEP] 按该记录末尾的唯一只读Python命令，检查`pseudo_spot_expression.csv`的形状、spot_id与ground truth的集合对应、数值非有限/负值/零行；再追溯表达由真实单细胞如何聚合及参考隔离代码。绝不删除文件或重新训练。

## 2026-11-22 最新：seqFISH+已证实为真实空间定位细胞聚合伪spot，下一步核查成员真值一致性

- [USER_WINDOWS_STDOUT] `cell_metadata_aligned.csv` 913×9（cell_uid、FOV、X/Y、type），`spot_cell_membership.csv` 514×9（cell到spot映射），`pseudo_spot_locations.csv` 70×10（bin_x/bin_y、grid中心及每spot n_cells），`pseudo_spot_ground_truth.csv`70×27（26细胞类型比例，示例是1/7或1/11的成员比例）。
- [DATA CLASS] 70个“spot”是从真实seqFISH+空间定位单细胞网格聚合得到的 **spatially informed pseudo-spots**，并非独立真实空间捕获spot。不能把本实验直接当作真实spot定量外部验证；但确有真实空间来源，价值不同于完全随机混合模拟。五FOV不构成独立生物学重复。
- [RECORDED] [四份本地CSV首审及下一步只读命令](CARR-lite-V2/experiments/records/2026-11-22_seqfishplus_pseudospot_provenance_first_check.md)。
- [NEXT SINGLE STEP] 用户Windows核对metadata/membership cell ID唯一、membership包含于metadata、70个spot的ID匹配、每spot n_cells、26类ground_truth按member counts重算一致。仍需审视399条未归属metadata的筛选原因、表达构建流程、nested排除源码；不重训练。

## 2026-11-22 最新：seqFISH+ 完整5-FOV历史结果与20条nested审计读完

- [USER_WINDOWS_STDOUT] 15行FOV指标及20条嵌套参考审计完整获取，见[全量终端转录](CARR-lite-V2/experiments/records/2026-11-22_seqfishplus_full_fov_metrics_and_nested_audit.md)。
- [FOV EFFECT] `V2_HGBC_Gate_a50` vs Tangram：JSD改善5/5、singleton RMSE/AUPRC/AUROC各改善4/5。FOV2虽然JSD改善0.430034→0.417433，但singleton RMSE恶化0.148069→0.157866、AUPRC下降0.293444→0.247989、AUROC下降0.653900→0.629039。必须完整保留。
- [NESTED REFERENCE] 18个训练FOV组合`used`，2个因缺L3被`skipped`。20行两个overlap字段均记录0；这仅为审计字段，不证明不存在其它泄漏，也不说明已验证真实spot来源。
- [NEXT SINGLE STEP] 用户在Windows本地只读查看`cell_metadata_aligned.csv`、`spot_cell_membership.csv`、`pseudo_spot_locations.csv`、`pseudo_spot_ground_truth.csv`的形状/列名和样本行，以厘清真实单细胞与聚合伪spot来源。具体单命令见上述完整记录末尾。
- 暂不训练、不重跑历史模拟、不造空间预测图，也不以5FOV或70spot声称独立生物学显著性。

## 2026-11-22 最新：找到seqFISH+五FOV历史数据，下一步完整fold/audit只读审查

- [USER_WINDOWS_STDOUT] 用户找到 `D:\Research\STdeconv_benchmark\data\groundtruth\seqfishplus_cortex_real_spatial_noleak` 内 fold_manifest (5×8)、metrics_by_fold (15×12)、nested_reference_leakage_audit (20×10) 和 pseudo_spot、cell membership 等CSV。
- [FIRST_READ] 五FOV共70spot、514保留目标细胞；manifest每折报告与reference重叠0。可见FOV2 `AbundanceOnly` 三项指标比Tangram变差，**FOV2 HGBC_a50行尚未显示**。嵌套审计显示部分训练FOV因缺L3被跳过；尚未看到完整20行。
- [RECORD] [首轮实际用户日志](CARR-lite-V2/experiments/records/2026-11-22_seqfishplus_fov_first_read.md)。
- [NEXT SINGLE STEP] 用户Windows执行该记录末尾的一条只读Python命令，打印全部15行fold指标及20行nested审计，确认三分支FOV2/FOV3/FOV4实际指标、used/skipped数及所有overlap字段。
- 勿因目录名`real_spatial_noleak`认定完全真实spatial spot或无泄漏；需审视`pseudo_spot_ground_truth.csv`及membership来源。暂不训练、不重跑模拟消融、不绘制空间点位图。

## 2026-11-22 最新：简单校准第6项13-base配对检查完成；下一步真实FOV证据定位

- [USER_WINDOWS_STDOUT] `BASE PAIR CHECK PASS: 26 method-base units`。RCTD HGBC_a30 vs Ridge12 RMSE改善8/13、AUPRC改善11/13；CARD vs Ridge12 RMSE改善6/13、AUPRC改善5/13。其他四组数据、均值差与负结果见 [13-base配对汇总](CARR-lite-V2/experiments/records/2026-11-22_simple_controls_13base_paired_summary.md)。
- [CONCLUSION_BOUNDARY] RCTD上CARR有部分优势，但AbundanceOnly RMSE稍优；CARD上CARR未普遍优于Ridge/Isotonic，且原始CARD的检测指标仍优于校准后。仅模拟场景描述统计，不保证真实FOV泛化或统计显著。
- [NEXT] 进入Claude原计划第2/3项：优先**查找本地已有seqFISH+ 5 FOV的原始评估CSV和划分依据**，只读列出相关文件路径，不急于新训练。第6项的逻辑回归/固定阈值替代仍未做，后续有需要再按预先固定规则补。
- 仍一次一条Windows PowerShell命令；不自动控制电脑、不加空间点位图、不重复已完成训练。

## 2026-11-22 最新：简单基线与CARR总体均值/原版指标对齐已完成，下一步13 base配对

- [USER_WINDOWS_STDOUT] `CHECK PASS: 312 simple rows, 520 CARR rows`；`ORIGINAL PARITY PASS`，两次独立批次的原版RCTD/CARD五指标在同场景完全一致，允许描述性比较。
- [RESULT] 严格四类别留出下 RCTD `HGBC_a30` RMSE 0.03236/AUPRC 0.55619 优于Ridge12 0.03311/0.54719和Isotonic1D 0.03320/0.54062；但RCTD AbundanceOnly RMSE 0.03228略好于HGBC。
- [CARD_NEGATIVE_RESULT] CARD Ridge12 RMSE 0.03280略优于HGBC_a30 0.03297；Isotonic1D AUPRC 0.54839优于HGBC 0.54521，原版CARD AUPRC 0.55189和Recall 0.14612均好于所有校准器。所有比较都需完整报告，不能只报RMSE下降。
- [RECORD] [四份CSV终端均值完整转录与解释](CARR-lite-V2/experiments/records/2026-11-22_simple_controls_fair_comparison.md)。
- [NEXT SINGLE STEP] 用户Windows只读汇总：以13个 `held_out_base` 为配对单元，四深度先取均值，统计HGBC_a30相对Ridge12/Isotonic1D/AbundanceOnly/Original目标RMSE与AUPRC改善base数并报告差值。禁止将52个视图误作为独立重复。

## 2026-11-22 最新：简单校准对照双方法均正式完成；下一步仅只读指标对齐比较

- [USER_WINDOWS_STDOUT] CARD 简单校准正式运行末尾 `FINISHED 156 result rows`，输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\CARD`；RCTD 前一轮亦完成 156 行。两法合计 312 评价行尚未逐行读取，不能宣称哪种简单基线更优。
- [RECORDED] [CARD 正式运行日志](CARR-lite-V2/experiments/records/2026-11-22_card_simple_controls_run.md)及[RCTD 运行日志](CARR-lite-V2/experiments/records/2026-11-22_rctd_simple_controls_run.md)。
- [NEXT SINGLE STEP] 在研究者 Windows 本地只读 4 份 `metrics_by_scenario.csv`：RCTD/CARD 简单校准（312行）与严格类别留出CARR（520行），检查 52 视图×方法数、五指标缺失及Original在两批评价的种子/指标一致性；之后才同场景对照 Ridge12、Isotonic1D、AbundanceOnly、固定HGBC_a30。继续保留 CARD 检测变差的负结果。
- 不重跑训练，不增加空间点位图。

## 2026-11-22 最新：RCTD 简单校准对照正式运行完成，CARD Dry-run 下一步

- [USER_WINDOWS_STDOUT] RCTD `simple_calibration_category_holdout.py` 正式运行完成，终端 `FINISHED 156 result rows`，输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\RCTD`。
- [RECORD] [2026-11-22 RCTD 简单基线正式运行日志](CARR-lite-V2/experiments/records/2026-11-22_rctd_simple_controls_run.md)。仅运行成功，尚未读取新指标 CSV。
- [NEXT ONE STEP] 用户在 Windows PowerShell 执行 `python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\simple_calibration_category_holdout.py" --method CARD --dry-run`。通过后再给 CARD 正式运行命令；两法都完成后再读取简单基线性能，与旧四类别留出下的 CARR 对照。
- 仍不增加空间预测点图、不覆盖旧结果。156 行=52模拟视图×3方法，不构成独立生物重复。

## 2026-11-22 最新：RCTD 简单基线 Dry-run PASS；下一步正式运行

- [USER_WINDOWS_STDOUT] `simple_calibration_category_holdout.py --method RCTD --dry-run`：52 views /13 bases，stable train36/test16，medium/confusable/lowref 各train40/test12，`SPLIT CHECK PASS`，`CONTROLS: Ridge12, Isotonic1D`，`DRY RUN PASS — no files written`。
- [RECORD] [本轮原始日志](CARR-lite-V2/experiments/records/2026-11-22_rctd_simple_controls_dry_run.md)。没有训练或指标；12维 Ridge 包含已知模拟深度，真实部署不能假设可用。
- [NEXT ONE STEP] 用户本地正式运行 `python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\simple_calibration_category_holdout.py" --method RCTD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1"`，预期每法156行（52视图×3）。
- 禁止覆盖旧结果、不得先声称基线改善。RCTD成功后再 CARD dry-run。

## 2026-11-22 最新：第4项类别留出配对已完成；进入第6项简单校准器对照

- [USER_WINDOWS_STDOUT] 将旧逐 base vs 新严格整类别留出 `HGBC_a30` 按场景ID配对，`PAIR CHECK PASS: 104 views, 26 method-base pairs`。分别先对各13个base内4深度平均：CARD 严格划分目标RMSE变差 **13/13**，AUPRC变差 **13/13**；RCTD 目标RMSE变差 **13/13**，AUPRC变差 **7/13**。四类别具体差值见 [归档数据](CARR-lite-V2/experiments/records/2026-11-22_category_vs_base_paired_counts.md)。这是模拟场景级描述统计，不能称独立生物学重复。
- [NEW CODE COMMITTED, NOT RUN] 原计划第6项简易后校准基线：`Ridge12`（12维输入标准化 + Ridge, alpha=1.0）与 `Isotonic1D`（基于 raw target abundance 单调校准），两法均复用原 local confusion projection、四类别留出、评价随机种子。脚本 [simple_calibration_category_holdout.py](CARR-lite-V2/experiments/simple_calibration_category_holdout.py)，[预注册协议](CARR-lite-V2/experiments/records/2026-11-22_simple_controls_protocol.md)。**没有运行新脚本，不能报新指标**。
- [NEXT SINGLE STEP] 用户 Windows 先 `git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only`，成功后再给 `RCTD --dry-run`。之后依次 RCTD run → CARD dry-run/run → 与原HGBC_a30同视图比较。
- 用户明确不做空间预测点位图，不重复十组消融；保存负结果，包括 CARD 在严格类别留出检测指标下降。

## 2026-11-22 最新：四类别留出指标已检查，下一步旧协议逐场景配对

- [USER_CONSOLE] 用户终端 `CHECK PASS: 520 rows, 10 groups, 52 rows each`，十组×五指标总体均值与四类别 Original/HGBC_a30 均值已保存 [原始控制台转录与风险](CARR-lite-V2/experiments/records/2026-11-22_category_holdout_metrics_console.md)。原520行 CSV 未上传，不能声称独立复算。
- [RESULT] 新严格划分 CARD HGBC_a30 Target RMSE 0.03297 对原 CARD 0.03720改善；**Balanced AUPRC 0.54521 对原 CARD 0.55189 恶化，Recall 0.13832对0.14612恶化**。RCTD target_RMSE 0.03236对原0.05789改善，AUPRC 0.55619对原0.54487改善，但 matrix_RMSE 0.09012对0.08986略差。
- [STRICT vs OLD BASE-HOLDOUT] CARD HGBC_a30 target_RMSE 0.03137→0.03297，AUPRC 0.55561→0.54521；RCTD target_RMSE 0.03096→0.03236，AUPRC 0.55710→0.55619。上述仅描述性均值。
- [NEXT SINGLE ACTION] 用户本地只读对齐同一 `scenario_id` 的新/旧 `HGBC_a30`，按13个held_out_base先聚合四深度，报告逐base与按类别变化。保留 CARD 检测变差的负结果；不重训练、不加空间点图。

## 2026-11-22 最新：严格类别留出 RCTD/CARD 均运行成功，下一步只读统计

- [USER_WINDOWS_STDOUT] CARD 正式运行尾部 `FINISHED 260 result rows`、输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\CARD`；此前 RCTD 同样完成 260 行。两法共预期 520 行，仍待读取两个 CSV 验证与比较数值。
- [RUN RECORDS] [RCTD](CARR-lite-V2/experiments/records/2026-11-22_rctd_category_holdout_run.md)；[CARD](CARR-lite-V2/experiments/records/2026-11-22_card_category_holdout_run.md)。
- [NEXT SINGLE STEP] 用户本地读取两份 `metrics_by_scenario.csv`，检查每基础法五种方法各 52 行、输出整体与按 held-out category 的五指标均值。然后再与逐 base 留出比较，禁止凭当前尾部日志推断效果。
- 不再重复消融，不补空间预测地图，继续 Claude 原八项补实验计划。

## 2026-11-22 最新：CARD 类别留出 dry-run PASS，等待正式运行

- [USER_WINDOWS_STDOUT] CARD 类别留出 `--dry-run`：四折 stable train36/test16，medium/confusable/lowref 各train40/test12；`INPUT CHECK PASS: CARD 52 scenario views / 13 bases`，`SPLIT CHECK PASS`，`DRY RUN PASS — no files written`。
- [GITHUB] [CARD dry-run 实验记录](CARR-lite-V2/experiments/records/2026-11-22_card_category_holdout_dry_run.md)；RCTD 正式运行此前已完成260行。
- [NEXT SINGLE STEP] 用户 PowerShell 正式运行 `python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\category_holdout_carr_v2.py" --method CARD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1"`。
- 用户 dry-run 之后另运行了一次 `& d:\paper\ST_Benchmark_Planning\mvp\.venv\Scripts\Activate.ps1`；未提供新的提示符，**不能断言环境激活成功或失败**。如果正式运行报模块缺失等错误，先看原始日志，绝不覆盖已有结果。

## 2026-11-22 最新：RCTD 类别留出正式运行成功，下一步 CARD dry-run

- [USER_WINDOWS_STDOUT] RCTD 四类别留出正式执行尾部为 `FINISHED 260 result rows`，输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\RCTD`；数据指标尚未汇总，不能断言泛化性能。
- [记录](CARR-lite-V2/experiments/records/2026-11-22_rctd_category_holdout_run.md)；此前 RCTD dry-run 记录亦保留。
- [NEXT SINGLE STEP] 用户手动运行 `python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\category_holdout_carr_v2.py" --method CARD --dry-run`，期待 `INPUT CHECK PASS: CARD 52 scenario views / 13 bases`、`SPLIT CHECK PASS`、`DRY RUN PASS — no files written`。
- CARD dry-run 通过后，才给 CARD 正式运行命令；两法数据都齐全后再按四类别比较与旧 13-base 协议差异。

## 2026-11-22 实时进度：RCTD 严格类别留出 dry-run 通过

- [USER_WINDOWS_STDOUT] Git pull 后新脚本已经在 Windows 本地。RCTD 四类拆分输入检查通过：stable(16测试/36训练)、medium/confusable/lowref(各12测试/40训练)，共52视图13 base，`DRY RUN PASS — no files written`。
- [RECORDED] [本次 dry-run 记录](CARR-lite-V2/experiments/records/2026-11-22_rctd_category_holdout_dry_run.md)。**正式训练仍是 NOT_RUN**。
- [NEXT ONE STEP] 本地执行 `python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\category_holdout_carr_v2.py" --method RCTD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1"`。预期260行，独立目录，不许覆盖旧结果。若出现错误，先读日志再操作。

## 2026-11-22 日终存档：暂停执行，明日从 Git pull 接手

- 用户明确：今日到此为止；不增加空间预测点位图，按 Claude 原八项补实验计划继续。
- 以前确认完成的 CARR RCTD/CARD 各 Full + 四种特征输入消融（10 组）均已归档，**无需重跑**。
- [VERIFIED_USER_UPLOAD] 已读取用户上传的 `CARRliteV2_ablation_base_paired_20261121_v1.csv`：104 行、18 列、无缺失、无配对键重复，五项指标配对差值与原列计算一致；八组改善计数复核一致。已在 GitHub 保存 [104 行派生结果数据](CARR-lite-V2/experiments/records/2026-11-21_ablation_base_paired_104rows.csv)，commit `14f28811aa6de2d0b523652ddc2613d8011f5631`。逐52视图原始 CSV 尚未上传。
- 新严格类别留出脚本已提交远端 main，**Windows Git pull、dry-run、正式训练均未确认**。类别留出每种方法预计 4 折，stable/medium/confusable/lowref 各留出一次。
- **NEXT ONE STEP（下次开工后给）**：`git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only`。收到成功日志后，仅给 RCTD 类别留出 dry-run；不直接训练或覆盖旧批次。
- [2026-11-22 日记与交接要点](RESEARCH_JOURNAL/2026-11-22.md)。下次先读 AGENTS / PROJECT_STATE / 本日日记，再读类别留出脚本；不可将工作计划描述为执行结果。

## 2026-11-22 当前唯一执行项：CARR 严格类别留出（Claude 第 4 项）

- 用户决定：**不补空间预测点位图**，仅按原补实验八项计划推进。
- [SCRIPT_COMMITTED_NOT_RUN] 新脚本 [category_holdout_carr_v2.py](CARR-lite-V2/experiments/category_holdout_carr_v2.py) 与 [预设协议](CARR-lite-V2/experiments/records/2026-11-22_category_holdout_protocol.md) 已在 main；**尚未取得本地 dry-run 或训练结果**。
- 四类 stable(16 views) / medium(12) / confusable(12) / lowref(12) 各留出一次，训练其余三类；分别验证 RCTD/CARD、输出 260 rows 每法、独立目录且禁止覆盖旧批次。
- 下一人工步骤：用户在 Windows 手动 `git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only`；回报输出，再发 RCTD dry-run 单命令。

## 104 行按基础场景配对差值 CSV 已在用户本地成功导出（2026-11-22）

- [USER_CONSOLE_EXPORT_LOG] 终端：`WROTE D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_base_paired_20261121_v1.csv ROWS 104`。
- 配置：RCTD/CARD × 4 特征组消融 × 13 held_out_base，固定 HGBC_a30，先合并四深度均值，记录 Full / 消融五项指标及配对差值。
- [导出日志记录](CARR-lite-V2/experiments/records/2026-11-22_base_paired_export_log.md)；文件**尚未上传本对话或仓库，未做逐行复核**。
- **下一步：请用户上传该本地 CSV；直接核验并绘制 SVG 矢量论文图。停止添加新训练。**

## 13-base 配对方向计数已完成（2026-11-21）

- [USER_CONSOLE_SUMMARY] 研究者先在每个 `held_out_base` 内对四档深度取均值，固定 HGBC_a30，将 8 个消融组合分别与 Full 做严格不等号的改善计数。
- [全部 8 组计数和解释](CARR-lite-V2/experiments/records/2026-11-21_ablation_by_base_counts.md)：CARD 的 Target RMSE 改善数（no_confusion/no_depth/no_marker/no_residual）= `6/6/6/4`（每组分母 13）；RCTD = `7/5/2/5`；AUPRC 详见记录。
- [NEXT] **导出 104 行基础场景配对效应 CSV**（2 方法 × 4 消融 × 13 base），含 Target RMSE 和 AUPRC 原值/差值，方便下步画可编辑 SVG 并做按组统计；不再增加训练。

## CARR 两方法五配置：10 组消融均值齐备（2026-11-21）

- [USER_CONSOLE_SUMMARY] CARD `no_marker_features` 终端运行 `FINISHED 260 result rows`，RCTD 同项亦已完成。研究者读取两种基础方法×Full/No_depth/No_residual/No_confusion_features/No_marker_features，固定 HGBC_a30，10 组各 52 场景。
- [10 组指标报告](CARR-lite-V2/experiments/records/2026-11-21_five_config_ablation_summary.md)及[10 行用户终端数据](CARR-lite-V2/experiments/records/2026-11-21_five_config_console_means.csv)；原始 CSV 尚未上传，不能声称独立复算。
- [RESULT] 去 marker 的 CARD 平均 target_RMSE `0.03137→0.03137`（显示精度一致）、AUPRC `0.55561→0.55645`；RCTD target_RMSE `0.03096→0.03106`、AUPRC `0.55710→0.55755`。不允许选择性报告。
- [NEXT] **停止新增特征消融训练**，以 13 个 held_out_base 聚合四种深度，计算相对 Full 的配对变化和改善场景计数，之后制作可编辑 SVG 结果图、论文结果段。待统计与图表整理，再回 CTW-RF 其他计划实验。

## RCTD no_marker_features 实验已完成（2026-11-21）

- [RUN_LOG_CONFIRMED] RCTD `--ablation no_marker_features` dry-run 通过 52 场景，正式运行 `FINISHED 260 result rows`，输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_marker_features`。
- [RCTD 运行记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_marker_features_v1.md)。尚未读取最新消融指标 CSV，**不作性能改善声明**。
- [NEXT] CARD `no_marker_features --dry-run` → CARD 正式实验 → 固定 HGBC_a30 合并两方法 × 五配置的均值比较；保留所有负结果。

## RCTD/CARD 四配置八组指标已由用户汇总（2026-11-21）

- [USER_CONSOLE_SUMMARY] 用户固定 `HGBC_a30`，读取 RCTD/CARD × Full/No_depth/No_residual/No_confusion_features 八组各 52 场景指标。
- [完整均值分析](CARR-lite-V2/experiments/records/2026-11-21_four_config_ablation_summary.md)及 [八行控制台 CSV](CARR-lite-V2/experiments/records/2026-11-21_four_config_console_means.csv)。
- No_confusion_features 对比 Full：CARD target_RMSE `0.03137→0.03110`、AUPRC `0.55561→0.55432`、Recall `0.14690→0.14341`；RCTD target_RMSE `0.03096→0.03068`、AUPRC `0.55710→0.55483`、Recall `0.14184→0.13750`。**丰度 RMSE 改善与检测性能下降同时存在**。
- [NEXT] 按既定清单进行最后的 `no_marker_features` 特征组消融，先 RCTD `--dry-run`，再正式运行，随后 CARD；不要用 Full 优势或事后选型掩盖负结果。

## CARD no_confusion_features 成功运行（2026-11-21）

- [RUN_LOG_CONFIRMED] CARD `--ablation no_confusion_features` dry-run 通过 52 场景；正式运行用户终端末尾 `FINISHED 260 result rows`。
- 输出：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_confusion_features`，原始指标 CSV 尚未由仓库读取。
- [CARD 消融执行记录](CARR-lite-V2/experiments/records/2026-11-21_card_no_confusion_features_v1.md)；和 [RCTD 同项记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_confusion_features_v1.md)。
- [NEXT] **现在先汇总 Full / No_depth / No_residual / No_confusion_features × RCTD/CARD 八组 `HGBC_a30` 指标**。性能变化未知；先读取 CSV 再叙述结果。

## RCTD no_confusion_features 执行结果（2026-11-21）

- [RUN_LOG_CONFIRMED] RCTD `--ablation no_confusion_features` dry-run 通过（52 场景）；用户正式运行末尾为 `FINISHED 260 result rows`，输出目录 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_confusion_features`。
- [RCTD 运行记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_confusion_features_v1.md)。尚未读取新消融的实际指标，不作性能结论。
- [NEXT] CARD 同项消融 `--dry-run` 后再正式执行；不覆盖已有输出。

## CARR 双方法三配置消融均值（2026-11-21）

- [USER_CONSOLE_SUMMARY] CARD 现有 no_residual 的 `run_config.json` 核验为 `CARD no_residual`；同时读取 2 方法 × Full/No_depth/No_residual、固定 `HGBC_a30`，各 52 行指标。
- [三配置比较分析](CARR-lite-V2/experiments/records/2026-11-21_three_config_ablation_summary.md)及 [六行均值转录 CSV](CARR-lite-V2/experiments/records/2026-11-21_three_config_console_means.csv)。
- `target_RMSE`：CARD Full/No_depth/No_residual 为 `0.03137/0.03139/0.03163`；RCTD 为 `0.03096/0.03097/0.03114`。残差特征移除的平均误差变化大于深度特征移除，但 AUPRC 不同方法方向不一致；仅描述统计。
- [NEXT] 按既定消融清单执行 RCTD `no_confusion_features` 的 dry-run，再由用户回报结果决定正式运行；`no_marker_features` 后续安排。

## CARD no_residual 既有结果目录（2026-11-21）

- [USER_CONSOLE_DIR_CHECK] CARD no_residual 正式命令尝试遇到 `FileExistsError`；目标目录已有 52 个场景子目录、260 条 `metrics_by_scenario.csv` 记录和 `run_config.json`（两文件时间 18:48:48）。因此**本次尝试没有运行训练**，既有结果已达到预期规模。
- [已存在输出记录](CARR-lite-V2/experiments/records/2026-11-21_card_no_residual_existing_output.md)；尚未核对 JSON 配置和四份指标实际值。
- [NEXT] 先验证 CARD 配置确为 no_residual，再读取 2 方法 × 3 配置的 HGBC_a30 五项均值；**不运行 `--force`，不重训。**

## RCTD no_residual 消融完成（2026-11-21）

- [RUN_LOG_CONFIRMED] RCTD `--ablation no_residual` 输入验证通过，用户正式实验日志末尾显示 `FINISHED 260 result rows`。
- 本地输出：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_residual`，原始 CSV 尚未读取。
- [实验记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_residual_v1.md)；还不能判断特征去除对性能的影响。
- [NEXT] CARD no_residual `--dry-run` → CARD no_residual 正式运行 → 固定 HGBC_a30 对照 Full / No-depth / No-residual。

## no_depth 消融指标汇总（2026-11-21 用户终端）

- [USER_CONSOLE_SUMMARY] 固定 HGBC_a30，四组各 52 场景：CARD full/no_depth target_RMSE `0.03137/0.03139`、AUPRC `0.55561/0.55607`；RCTD full/no_depth target_RMSE `0.03096/0.03097`、AUPRC `0.55710/0.55681`。
- [数值及边界](CARR-lite-V2/experiments/records/2026-11-21_no_depth_ablation_mean_results.md)与 [4 行终端均值 CSV](CARR-lite-V2/experiments/records/2026-11-21_no_depth_console_means.csv)。四种深度属于同一基础场景；五位小数无法证明严格等效。
- [NEXT] 按当前队列继续 RCTD `no_residual` 特征组消融：先 `--dry-run`，通过再正式运行；然后 CARD，同样不覆盖 full/no_depth。
  
## RCTD + CARD No-depth 消融均已运行完成（2026-11-21）

- [RUN_LOG_CONFIRMED] CARD `--ablation no_depth`：52 场景输入检查通过，正式运行 `FINISHED 260 result rows`；本地输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_depth`。
- [CARD 运行记录](CARR-lite-V2/experiments/records/2026-11-21_card_no_depth_v1.md)与 [RCTD 运行记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_depth_v1.md)均已在仓库归档。
- [NEXT] 本地读取四份指标 CSV（RCTD/CARD × full/no_depth），固定 `HGBC_a30` 对照，先看五项描述性指标；原始 CSV 尚未读入仓库，性能影响未知。

## RCTD No-depth 特征消融（2026-11-21，用户运行日志）

- [RUN_LOG_CONFIRMED] RCTD `--ablation no_depth` 52 场景 dry-run 通过；正式运行末尾 `FINISHED 260 result rows`，输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_depth`。
- [运行日志](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_depth_v1.md)：原始 CSV 尚未读取，不得断言消融后的性能变化。
- **两种方法的 no_depth 消融均运行完成；下一步读取四份指标 CSV 比较。**

# 两篇 SCI 扩充：实验执行队列（2026-11-21）

> 当前决策：**优先按既定扩充清单交付新的可比较实验**。除非发现会直接导致错误运行/污染数据的阻断问题，暂不插入额外的全面审计任务；已有风险统一保留到最后的科研验收阶段。任何实验仍不得使用测试真值调参、伪造结果、覆盖历史记录。

## 当前状态

| 优先级 | 论文 | 实验 | 交付物 | 目前状态 |
|---|---|---|---|---|
| P1 | CTW-RF | 全局非负 stacking + 等权 + 原单方法 | `global_stacking_oof.csv`、`metrics_overall.csv`、`metrics_by_fold.csv`、`global_weights_by_fold.csv` | **用户日志确认运行成功；原始输出仍在本地** |
| P1 | CARR-lite V2 | RCTD + CARR 三分支（12 个 base 训练/1 个 base 留出） | 每场景预测 + `metrics_by_scenario.csv` | **用户日志确认 52 场景/260 条结果运行完成；待读取指标** |
| P2 | CARR-lite V2 | CARD + CARR 三分支 | 同上 | **用户日志确认 52 场景/260 条结果完成；待性能汇总** |
| P2 | CTW-RF | 更多随机划分、配对结果及图表 | CSV、SVG、配置与日志 | **计划** |
| P3 | CARR-lite V2 | 简单校准方法、特征消融和部署敏感性 | 公平对照 CSV | **计划** |
| P3 | CTW-RF | EnDecon 等最近邻集成基线及 DLPFC 应用扩展 | 可比较指标 | **计划；实现前需核对原文接口** |
| 终期 | 两篇 | 原始结果复核、泄漏/独立性审查、论文一致性与投稿政策 | 审计报告与正式论文表格 | **安排在扩充实验之后** |

## 13 个 base 分组配对结果 / 消融准备（最新）

- [USER_CONSOLE_SUMMARY] 统一选择 `HGBC_a30`，在每个 `held_out_base` 内将四种深度均值与 Original 配对：**RCTD target_RMSE 改善 13/13、balanced_AUPRC 改善 10/13；CARD target_RMSE 改善 13/13、balanced_AUPRC 改善 9/13**。
- [分组结果记录](CARR-lite-V2/experiments/records/2026-11-21_cross_method_by_base.md)；CARD 分组逐行日志前半段被截断，未凭空补全。
- [CODE_READY / NOT_RUN] 已对 `CARR-lite-V2/experiments/cross_method_carr_v2.py` 新增 `--ablation` 可选特征消融（提交 `f5e3ead23bb122027a5c333d35021f283c2fddac`）；默认无消融不改变历史实验。先跑 `no_depth` 敏感性，再视结果开展 residual/confusion/marker feature 消融。
- [NEXT] 用户本机先同步 GitHub 最新脚本，再执行一条 dry-run；**新消融尚未在本地测试**。

## 跨方法性能汇总已取得（用户终端 2026-11-21）

- [汇总记录：RCTD/CARD 指标与解释](CARR-lite-V2/experiments/records/2026-11-21_cross_method_mean_results.md)
- [十行均值转录 CSV](CARR-lite-V2/experiments/records/2026-11-21_cross_method_console_means.csv)
- [USER_CONSOLE_SUMMARY] 用户从本地 520 行结果读取两方法×五个输出变体的各指标均值：RCTD 原始 target_RMSE `0.05789`，CARR a15 `0.03089`；CARD 原始 `0.03720`，CARR a30 `0.03137`。
- [TRADEOFF] RCTD 加 CARR 的矩阵 RMSE 略增，不能称所有指标改善；CARD a15 的 recall 也略降。
- [NEXT] 按 `held_out_base` 聚合四深度后，做 13 个基础场景的配对改变量描述和改善场景计数；这属于扩充实验结果分析，不作为额外全面审计。

## CARR CARD 新增运行记录（2026-11-21）

- [CARD 运行记录](CARR-lite-V2/experiments/records/2026-11-21_card_cross_method_v1.md)：dry-run 通过，用户终端确认 `FINISHED 260 result rows`。
- CARR 两种新基础方法 RCTD + CARD 都已运行结束，合计 520 条方法—场景记录；**尚无可读指标 CSV 数值，不能声明改善**。
- **两个指标表已由用户读取并在仓库归档汇总；逐 base 配对计数也已取得，接下来做 no_depth 特征消融。**

## CARR RCTD 新增运行记录（2026-11-21）

- [RCTD 跨基础方法运行记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_cross_method_v1.md)：用户先报告 RCTD 52 场景 `DRY RUN PASS`，后提供正式执行 `Completed` 至 B13 第四深度，末尾 `FINISHED 260 result rows`。
- 本地输出：`D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\RCTD`；**尚未独立读取 `metrics_by_scenario.csv`，不做性能提升声明**。
- **当前两项均已由日志确认完成；下一项为同口径指标汇总。**

## 首项成功记录（2026-11-21）

- [CTW 全局 stacking 的本地执行记录](CTW-RF/experiments/records/2026-11-21_global_stacking_v1.md)：selftest、dry-run、真实 2000 spot×19类×6方法五折均由用户返回成功日志。
- GlobalStacking（本次终端日志）：JSD 0.113543，matrix_RMSE 0.048965，aggregated_celltype_RMSE 0.867207；原始结果位于本地 `D:\Research\STdeconv_benchmark\results\CTWRF_GlobalStacking_20261121_v1`，**尚未读取原始 CSV**。
- 历史 CTW Proposed_CV：JSD 0.101752、matrix_RMSE 0.041467、aggregated RMSE 0.725670（旧 GitHub CSV，未经此次复算）。
- **当前下一项：CARR CARD 跨基础方法读取检查（dry-run）**；若数据布局与脚本默认不一致，先定位真实预测文件位置，不重跑已有历史基线。

## 已交付的脚本

- [CTW 全局 Stacking 五折对照](CTW-RF/experiments/global_stacking_cv.py)
- [CARR RCTD / CARD 跨基础方法实验](CARR-lite-V2/experiments/cross_method_carr_v2.py)

**重要区分**：提交脚本只说明代码可供运行；没有可核实的本机执行日志与生成的 CSV，就不能勾选实验完成。CTW 脚本已经在用户 Windows 环境中完成自检、输入验证和一次真实实验运行；CARR 脚本仍待冒烟测试。

## CTW 下一执行步骤

脚本默认读取：

- `D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots\pseudo_spot_ground_truth.csv`
- 同目录下 `predictions/` 中的 `Tangram_self_benchmark.csv`、`RCTD_self_benchmark.csv`、`CellDART_self_benchmark.csv`、`CARD_self_benchmark.csv`、`Cell2location_self_benchmark.csv`、`SPOTlight_self_benchmark.csv`

先运行 `--selftest`（合成内存数据，无磁盘输出），再 `--dry-run`（只读检查数据），通过后执行五折对照并保存未覆盖的原始输出。默认随机种子 2026；文件缺失时先定位实际路径，不盲目补零。

## CARR 下一执行步骤

脚本默认寻找 `rarecell_52scenario_suite/scenario_views/scenario_view_manifest.csv`、52 个视图和每视图 `predictions/RCTD_self_benchmark.csv` 或 `CARD_self_benchmark.csv`。若实际历史预测存在于 `batch_runs/`，需经只读确认后用 `--prediction-template` 指向真实路径，而不是假定文件已经存在。

CARR 当前默认与原脚本一致：`confusion_k=3`、`marker_k=40`，保留受控模拟深度特征用于本次“跨基础方法”单变量扩展；移除深度特征属于后续**单独**实验，不能与替换基础方法同时变化。

预期单方法的输出根目录：
`rarecell_52scenario_suite/batch_runs/CARRliteV2_cross_method/<METHOD>/`。已有输出不会在缺少显式 `--force` 的情况下覆盖。

## 最低限度执行纪律

1. **一次只在用户 Windows 本机运行一条命令/短步骤**；GPT 可以在 GitHub 集中准备多个脚本和文档。
2. 每次记录执行命令、脚本 commit、输入路径、原始 stdout/stderr、输出 CSV、是否成功。
3. 若训练/预测阶段直接报错，先修使实验可运行的接口问题；一般性的原创性/论文审计统一留到终期。
4. 相同场景公平对比、固定分组留出、测试真值不用于训练，是执行基本条件，不视为“提前做全面审计”。
5. 未运行的实验始终标注 `PLANNED` 或 `CODE_READY`，不提前填写性能结果。
