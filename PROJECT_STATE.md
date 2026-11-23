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

## 2026-11-23 最新：EnDecon聚合核心移植版3池正式运行完毕，下一步读权重/无监督简单对照

- [USER_WINDOWS_STDOUT] 已正式运行`CTW-RF/experiments/ctw_endecon_aggregation_batch.py --run`，算法自检和输入检查通过；strong2、expanded4、full6均显示3轮迭代收敛，调度器`BATCH FINISHED 3 method pools x 3 ensemble variants; 18 CTW reference comparisons`。[本地运行原文](CTW-RF/experiments/records/2026-11-23_endecon_aggregation_run_results.md)。Python移植作者核心，不是官方R软件。
- [REAL_NUMBERS] strong2 EnDecon JSD .098996、matrixRMSE .056752；expanded4 .119340/.051988；full6 .233707/.073754。相比既有CTW SoftOpt的strong2 3seed均值JSD .114850/RMSE .052449、expanded4 .110677/.044521、full6 .101723/.041453：EnDecon在strong2的JSD优于CTW，RMSE劣于CTW，4池/6池则两项均落后。不能宣称CTW无例外全面领先；全6池大幅恶化原因仍待实际读取权重。
- [READ_PENDING] 本机`D:\Research\STdeconv_benchmark\results\CTWRF_EnDecon_aggregation_20261122_v1\endecon_weights_by_pool.csv`、`ensemble_metrics_by_pool.csv`、`endecon_diagnostics_by_pool.csv`尚未直接读取。strong2的EnDecon JSD几乎等于历史cell2location JSD仅提示权重可能集中，**非已经确认**。
- [NEXT SINGLE ACTION] Windows一条只读Python/PowerShell命令汇总三个CSV，展示每池权重分配、三种无监督聚合对照指标和迭代lambda/收敛状态；不重跑旧模拟实验。继续安排CARR真正跨数据集或CTW DLPFC泛化的整批实验，最终综合审计交Claude。
- [COMPLETED] CARR12、CTW GlobalStacking36配置、CTW主方法同折9配置和本次EnDecon3池聚合均完成，所有状态均来自用户Windows终端而非助手在其本地代跑。相关种子/方法池不是独立生物重复。

## 2026-11-22 最新：CTW完整配对指标已有数值，EnDecon作者融合核心3池批处理脚本已提交待运行

- [USER_WINDOWS_CSV_SUMMARY] CTW的3seed×3pool同折主方法比较完整JSD、matrix_RMSE、aggregate RMSE和拟合时间已由用户终端打印。[真实性能及9组配对计数归档](CTW-RF/experiments/records/2026-11-22_ctw_matched_fusion_metrics_from_user_console.md)。full6三seed均值CTW SoftOpt JSD 0.101723、matrixRMSE 0.041453、aggregateRMSE 0.725489；GlobalStacking 0.113531、0.048966、0.867231。CTW对Global/HardSelect的JSD与matrixRMSE均9/9改善，但JSD对InvRMSE_p2和EqualWeight仅6/9改善；软优化平均拟合0.331s/折，对比Global0.015s/折。种子/方法池均为技术相关条件，非独立生物重复。
- [LITERATURE_VERIFIED] 已直接查看Tu et al. 2023 *Bioinformatics* EnDecon DOI 10.1093/bioinformatics/btac825及`Zhangxf-ccnu/EnDecon/R/EnDeconv.R` `solve_ensemble`实现（加权中位数+全局L1距离/熵权重迭代）；不能把EnDecon称简单加权平均或混入另一个SunXQlab同名实现。
- [GITHUB_CODE_READY_NOT_RUN] 新增[CTW EnDecon加权中位数聚合对照批处理](CTW-RF/experiments/ctw_endecon_aggregation_batch.py)及[方案证据边界](CTW-RF/experiments/records/2026-11-22_endecon_aggregation_extension_protocol.md)。3方法池×EnDecon聚合/普通中位数/等权均值=9指标结果，再与已完成3seed CTW主方法/Global比较；复用现成六个预测，不要求重新运行所有基础方法。**Python按作者R核心移植，不是作者完整R软件运行，数值中位数平手约定可能不同；尚未Windows同步/dry-run/正式运行**。
- [NEXT SINGLE ACTION] 用户Windows一条PowerShell先`git pull --ff-only`再成功时新脚本`--dry-run`；通过后另条`--run`。已有CARR12、CTW36、CTW同折9不再重跑。
- [DEFERRED AUDIT] 用户要求先批量实验、最后Claude整体方法和论文审计，当前不插入前期审计；仍需对所有统计/文献/实验状态真实表述。

## 2026-11-22 最新：CTW-RF同折主方法对照9/9完成，SoftOpt JSD均优于GlobalStacking

- [USER_WINDOWS_STDOUT] `ctw_matched_fusion_comparisons_batch.py --dry-run`预检2000spots/19类/6方法通过后，用户正式`--run`完成**3seed×3pool共9个同折5fold实验、81行方法级摘要**；每种配置`optimizer_fallback_total 0`。终端9/9 SoftOpt JSD低于GlobalStacking。[原始控制台归档](CTW-RF/experiments/records/2026-11-22_ctw_matched_fusion_9_seed_pool_completed.md)。
- [RESULT] full6池 CTW SoftOpt JSD（seed2026/2027/2028）分别0.101752/0.101690/0.101727；GlobalStacking分别0.113543/0.113507/0.113544。strong2与expanded4三个seed JSD同样9/9占优；**仅同一伪spot数据多次划分，非9独立生物重复；尚未读取RMSE/逐折CSV**。
- [NEXT SINGLE ACTION] 用户Windows一条只读Python命令读取`D:\Research\STdeconv_benchmark\results\CTWRF_matched_fusion_20261122_v1\summary_metrics_by_seed_pool.csv`、`paired_differences_by_seed_pool.csv`及`fit_runtime_by_fold.csv`，汇总SoftOpt/Global JSD、matrix RMSE、aggregate RMSE、各对照配对方向和拟合时长。不再重跑9种实验，整体审计按用户要求后置。
- [WORKFLOW] 两篇已完成CARR12任务、CTW GlobalStacking36配置与CTW同折9配置；仅运行日志确认，原始CSV本机而非GitHub。随后继续原定EnDecon等最近邻集成、CTW真实数据扩展和CARR参考训练/留出FOV泛化。不能宣布尚未执行的实验完成。

## 2026-11-22 最新：CARR12项及CTW36配置实际汇总已收到；CTW主方法同折批处理已提交，待用户Windows运行

- [USER_WINDOWS_CSV_SUMMARY] 本地读取CARR `batch_run_status.csv`，12/12子任务均`success`，耗时89.929–187.534秒/任务；`batch_metric_means.csv`关键值R/C marker_k20 HGBC_a30分别RMSE .032125/.032742，AUPRC .559223/.548711；去depth RMSE .032353/.032992；CARD Threshold1D AUPRC .551166 但RMSE .037406，检测/定量权衡保留。所有12任务关键指标见[真实控制台汇总记录](CARR-lite-V2/experiments/records/2026-11-22_batched_carr_ctw_actual_console_results.md)。
- [USER_WINDOWS_CSV_SUMMARY] CTW `metrics_by_seed_pool_budget.csv`含36个GlobalStacking配置，full6/all在3种随机seed上JSD均值 .113531 (range .113507–.113544)、matrixRMSE均值 .048966 (.048960–.048973)；expanded4/all JSD均值 .113403、matrixRMSE .049586，强2/all JSD .116177、RMSE .052691。属于同一2000伪spot数据的CV重划分，不是独立供体；**不是CTW主方法复测**。[完整三seed摘要](CARR-lite-V2/experiments/records/2026-11-22_batched_carr_ctw_actual_console_results.md)。
- [CODE_COMMITTED_NOT_RUN] **新增CTW-RF 同折直接比较批处理**[ctw_matched_fusion_comparisons_batch.py](CTW-RF/experiments/ctw_matched_fusion_comparisons_batch.py)：按历史verifier的预定义SoftOpt（Proposed_CV）、InvRMSE_p2、HardSelect与GlobalStacking、EqualWeight、单方法，在相同5折下批量比较3 seeds×3 pool=9种设置；记录per-fold/per-seed结果、配对差值与模型拟合耗时。使用历史SoftOpt已选型属于探索性复测，不宣称独立选型验证。**尚未用户Windows git pull / dry-run / --run**。
- [NEXT SINGLE ACTION] Windows一条PowerShell连续命令先`git pull --ff-only`、仅拉取成功时执行新CTW脚本`--dry-run`；通过后下一轮`--run`。不要重跑已完成CARR12/CTW36配置。用户已明确最终审计由Claude在实验完成后集中处理。

## 2026-11-22 最新：两轮批处理运行完成（CARR12项+CTW36配置），下一步统一读指标

- [USER_WINDOWS_STDOUT] **CTW GlobalStacking敏感性批处理**预检2000 spots/19类/6方法通过，随后正式跑完3个seed×3个方法池×4校准样本量，终端`BATCH FINISHED 36 of 36 configurations; FAILED 0`。[2026-11-22运行记录](CTW-RF/experiments/records/2026-11-22_ctw_36configuration_batch_completed.md)。2028 seed，full6池+all预算终端JSD 0.113544、matrix_RMSE 0.048973，其余36组全部指标待读CSV。
- [USER_WINDOWS_STDOUT] **CARR**12个marker_k/confusion_k/no_depth/LogisticThreshold批次已经`BATCH FINISHED 12 jobs`。[运行记录](CARR-lite-V2/experiments/records/2026-11-22_pending_12job_batch_completed.md)，`batch_metric_means.csv`和`batch_run_status.csv`有本地输出路径但尚未读取具体数值。
- [EVIDENCE_BOUNDARY] 以上“完成”均指用户电脑**运行日志确认**，并非助手已下载48个任务结果CSV或独立复核。CTW36组只是GlobalStacking对照稳定性，不是CTW Proposed自身对照实验；随机种子不是独立生物样本。
- [NEXT SINGLE ACTION] 用户Windows **一条只读Python命令同时读取CARR批次状态、关键方法均值以及CTW的36配置分组均值/范围**，按真实CSV判断后续要补的EnDecon/CTW同折和CARR外部数据实验。**不要再跑已经完成的48任务**；遵守用户“先批实验，Claude最后集中审计”决定。

## 2026-11-22 最新：CARR 12任务正式批处理已完成，转 CTW 36配置

- [USER_WINDOWS_STDOUT] 用户本机运行`carr_pending_experiments_batch.py --run`，尾部`logistic_threshold CARD FINISHED 156 result rows`、`DONE ... elapsed_seconds 89.93`，最终`BATCH FINISHED 12 jobs`。原先12任务预检全为NEW，输入`BATCH PREFLIGHT PASS`，现可将CARR这一批标为**运行日志确认完成**。[归档](CARR-lite-V2/experiments/records/2026-11-22_pending_12job_batch_completed.md)。
- [METRICS_PENDING] `D:\Research\STdeconv_benchmark\results\CARRliteV2_pending_batch_20261122_v1\batch_metric_means.csv`与`batch_run_status.csv`本地已报告写入，尚未读取具体指标与每任务状态。按设计预期2912行评价记录，**未实际汇总CSV行数或性能变化**。
- [NEXT SINGLE ACTION] 转向CTW的36配置全局stacking敏感性批处理，用户本地先执行`python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_stacking_sensitivity_batch.py" --dry-run`；输入通过再独立一条`--run`。此批只补GlobalStacking对照稳定性，不能当CTW Proposed_CV同fold结果。
- [PRIORITY] 用户要求先完成原定补实验、不要逐项重开泄漏审计，实验末尾再由Claude集中审查；禁止覆盖旧数据、混淆报告与实际结果。

## 2026-11-22 最新决策：集中批量推进补实验（新任务优先；全面审计后置）

- [USER_DECISION] 用户明确要求先按最初Claude补实验清单**推进实验，不再逐步插入数据泄漏/论文全面审计**；所有实验跑完后再由Claude集中审查。同时希望一次写多个实验任务、减少Windows人工步骤。正常数据检查与非覆盖保护仍保留。
- [CODE_READY_GITHUB / NOT_RUN] 新建[CARR 12任务批处理](CARR-lite-V2/experiments/carr_pending_experiments_batch.py)和[逻辑回归+固定阈值对照](CARR-lite-V2/experiments/logistic_threshold_category_holdout.py)：RCTD/CARD各跑marker_k20/80、confusion_k1/5、严格category no_depth、LogisticPresence12与Threshold1D。新脚本语法编译与任务布局简单烟测已通过，**尚未Windows同步、dry-run或正式训练**。对应 [执行协议](CARR-lite-V2/experiments/records/2026-11-22_batched_extension_protocol.md)。
- [CODE_READY_GITHUB / NOT_RUN] 新建[CTW stacking 36配置批处理](CTW-RF/experiments/ctw_stacking_sensitivity_batch.py)：三个spot级划分seed×2/4/6方法池×100/200/500/all校准量，独立输出和失败日志；**尚未Windows运行**。此批仅扩展全局stacking对照稳定性，不能替代CTW-RF Proposed_CV同fold性能验证。
- [NEXT SINGLE ACTION] 用户Windows执行`git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only`同步新脚本；成功后给CARR批处理`--dry-run`，再`--run`一次性12任务，最后CTW 36配置批处理。执行阶段不能把计划写成已完成。
- 原先seqFISH+ 代码审计（builder第1–80、266+、runner等）**按用户决定暂缓**，不再占用执行队列；保留已有风险交给最后Claude验收，原始数据和评价边界不做无证据保证。

# PROJECT_STATE — CTW-RF × CARR-lite V2

- 更新：2026-11-22（Asia/Taipei）
- 阶段：**seqFISH+ builder源码第81–265行已由用户完整贴出：成员细胞表达按FOV网格求和，26类真值按成员类型计数，参考排除整外层FOV并检查cell ID重叠。尚未审查第1–80/266+行与模型训练runner，不能声称全流程无泄漏。**
- 当前仓库：`Hisery123/st-deconvolution-research`（公开，main）
- 注意：104 行用户上传的**按 base 派生 CSV** 已直接读取并复核差值/计数；但十份原始 52-view 指标 CSV、全部训练与模型权重**仍未直接取得或独立复算**。不得将文中叙述等同于所有实验已复现。

## 2026-11-22 日终交接（最新，冻结状态）

- [USER_DECISION] 用户明确结束今日工作、要求存档；**不补空间预测点位图**，继续 Claude 原八项补实验。
- [GITHUB_ARCHIVED] [104 行配对数据 CSV](CARR-lite-V2/experiments/records/2026-11-21_ablation_base_paired_104rows.csv) 已由用户上传文本存入 GitHub（commit `14f28811aa6de2d0b523652ddc2613d8011f5631`）。对上传文件直接检查：104×18，0 缺失，0 配对键重复，五种差值重算在浮点精度内一致；RMSE/AUPRC 八组改善计数全部与终端记录相符。数据是四深度按13 base 聚合的派生表，并非原始逐52视图结果。
- [RESEARCH_JOURNAL] [2026-11-22 归档与五点交接提醒](RESEARCH_JOURNAL/2026-11-22.md)；含输入路径、证据级别、原上传文件 SHA-256 `4d6f58bc549a6136fefa901174a063f0a908d2b327f66dc442ee85c651113d07`（GitHub 文本换行可能不同）。
- [CODE_READY_NOT_RUN] 严格类别留出脚本 commit `4da4c29076c757467d7704a151fca40c64c5fc13`，未获本地 Git pull / dry-run / 训练日志。不能声称新实验已执行；旧的十组消融无需重跑。
- [NEXT_SINGLE_ACTION] 下次唯一手动步骤：研究者 Windows 本地同步 `git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only`。成功后才能给 RCTD category holdout `--dry-run` 命令，随后再按计划安排训练。不应在日终额外启动工作。

## 2026-11-22 下一实验：严格类别留出（历史计划）

- 用户明确：不增加空间预测点位图；遵循 Claude 的八项补实验原计划。
- [SCRIPT_COMMITTED_NOT_RUN] [新独立验证脚本](CARR-lite-V2/experiments/category_holdout_carr_v2.py) 提交 main。[协议与证据边界](CARR-lite-V2/experiments/records/2026-11-22_category_holdout_protocol.md)。
- 4 折逐类别留出：stable(4 base/16视图)、medium(3/12)、confusable(3/12)、lowref(3/12)，总计13个base×4深度=52视图。RCTD/CARD 各独立重训。严格不覆盖旧的13-base实验。
- [NEXT] 用户手动 Git pull → RCTD dry-run → 正式运行，再轮到 CARD。无任何新类别留出结果可报告。
- 104 行按 base 配对表已经收到用户上传并曾核对结构，生成了本轮绘图数据；新实验不改变该表。

## 2026-11-22 按 base 配对结果导出完成（最新）

- [USER_CONSOLE_EXPORT_LOG] 用户执行修正后的 pandas 多对一合并导出，终端 `WROTE D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_base_paired_20261121_v1.csv ROWS 104`。
- **该条为上传前的历史记录，已被 2026-11-22 日终交接更新取代**：用户随后上传了文件，助手核验 104 行、18 列及差值和计数，且已将文本版派生 CSV 写入 GitHub。完整逐52视图的原始指标 CSV 仍未上传。
- [记录](CARR-lite-V2/experiments/records/2026-11-22_base_paired_export_log.md)。
- [NEXT] 用户上传该文件到对话后，核验 13-base 配对差值与此前改善方向计数，再制作可编辑 SVG 与 Results 文本；不增加训练。

## 2026-11-21 13-base 消融方向计数（最新）

- [USER_CONSOLE_SUMMARY] 对每个 `held_out_base` 聚合四档 depth，固定 `HGBC_a30`，严格比较各消融与 Full 的 Target RMSE / AUPRC。
- [RESULT] CARD：no_confusion / no_depth / no_marker / no_residual 的 Target RMSE 改善 base 数分别 `6/13, 6/13, 6/13, 4/13`，AUPRC 改善 `7/13, 7/13, 7/13, 5/13`。RCTD：Target RMSE 改善 `7/13, 5/13, 2/13, 5/13`，AUPRC 改善 `6/13, 4/13, 6/13, 6/13`。
- [RECORD] [8 组 base 计数记录](CARR-lite-V2/experiments/records/2026-11-21_ablation_by_base_counts.md)。严格改善计数之外可能存在持平，不能都叫恶化；没有独立生物学重复或统计检验结果。
- [NEXT] 提取 2×4×13=104 行按 base 聚合的配对差值 CSV，再做 SVG 图。不扩展新的特征消融训练。

## 2026-11-21 CARR 五配置消融全量均值已获得（最新）

- [RUN_LOG_CONFIRMED] CARD `no_marker_features` 正式运行末尾 `FINISHED 260 result rows`，输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_marker_features`。
- [USER_CONSOLE_SUMMARY] 用户读取 RCTD/CARD × 5 配置 `HGBC_a30` 的五项均值，每配置 52 个场景。CARD no_marker 相对 Full：RMSE `0.03137→0.03137`，AUPRC `0.55561→0.55645`；RCTD RMSE `0.03096→0.03106`，AUPRC `0.55710→0.55755`；其他指标与四组消融数据完整转录在下列两文件中。
- [REPORT] [10 组消融分析](CARR-lite-V2/experiments/records/2026-11-21_five_config_ablation_summary.md)，[10 行控制台转录 CSV](CARR-lite-V2/experiments/records/2026-11-21_five_config_console_means.csv)。原始 CSV 尚未直接进入仓库或独立复算；**不得把小幅均值差异称为显著**。
- [NEXT] 不再拓展特征消融；先做 13 base 配对变化与 SVG 绘图数据，再回 CTW-RF 计划扩充。

## 2026-11-21 RCTD no_marker_features 已完成（用户日志）

- [RUN_LOG_CONFIRMED] `--method RCTD --ablation no_marker_features --dry-run` 检查 52 场景通过；正式执行末尾 `FINISHED 260 result rows`。
- 本地结果目录：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_marker_features`。三项 marker 输入特征排除；其余算法模块保留。
- [RECORD] [RCTD 运行记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_marker_features_v1.md)。指标 CSV 未直接读取，尚不评价 no_marker 效果。
- [NEXT] CARD 同项 `--dry-run`，通过后正式运行；最终汇总十组固定 HGBC_a30 指标。

## 2026-11-21 八组消融对照实际指标（最新）

- [USER_CONSOLE_SUMMARY] 用户从八份原始 `metrics_by_scenario.csv` 中筛选 `HGBC_a30`，每组 52 条记录，汇总 `target_RMSE`、`target_MAE`、`balanced_AUPRC`、`recall_at_10pct_FPR`、`matrix_RMSE`。
- CARD：Full vs No_confusion_features，target_RMSE `0.03137→0.03110`，AUPRC `0.55561→0.55432`，Recall `0.14690→0.14341`。
- RCTD：Full vs No_confusion_features，target_RMSE `0.03096→0.03068`，AUPRC `0.55710→0.55483`，Recall `0.14184→0.13750`。
- [INTERPRETATION] 去掉混淆特征使丰度误差改善，但检测指标下降，属于可信的方向性权衡而不是“全面提升”。仍为用户终端五位小数的场景描述性均值。
- [RECORD] [八组消融汇总](CARR-lite-V2/experiments/records/2026-11-21_four_config_ablation_summary.md)及 [CSV 控制台转录](CARR-lite-V2/experiments/records/2026-11-21_four_config_console_means.csv)；本地原始指标 CSV 未上传，未作独立复算。
- [NEXT] RCTD `--ablation no_marker_features --dry-run`，随后 RCTD/CARD 同项消融，保持当前执行优先级。

## 2026-11-21 CARD no_confusion_features 运行成功（最新）

- [RUN_LOG_CONFIRMED] CARD `--ablation no_confusion_features --dry-run` 输入检查 52 场景通过；用户正式执行日志 `FINISHED 260 result rows`，输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_confusion_features`。
- [RECORD] [CARD 执行记录](CARR-lite-V2/experiments/records/2026-11-21_card_no_confusion_features_v1.md)。
- [NEXT] 由用户在本地汇总固定 `HGBC_a30` 八组指标（RCTD/CARD × Full/No_depth/No_residual/No_confusion_features）；不提前声明混淆特征消融效果。

## 2026-11-21 RCTD no_confusion_features 运行成功（最新）

- [RUN_LOG_CONFIRMED] RCTD `--ablation no_confusion_features --dry-run` 52 场景通过，排除四个混淆相关输入特征；正式运行 `FINISHED 260 result rows`。
- [LOCAL_OUTPUT] `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_confusion_features`。
- [RECORD] [本轮执行日志](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_confusion_features_v1.md)；未读取该消融 CSV 的具体指标，不推断效果。
- [NEXT] CARD 同配置 dry-run，随后正式运行；保持原有 Full/No-depth/No-residual 结果不变。

## 2026-11-21 双基础方法三配置消融结果（最新）

- [USER_CONSOLE_SUMMARY] CARD no_residual `run_config.json` 已核实 `base_method=CARD`、`ablation=no_residual`。六组 `HGBC_a30` 指标各 52 条数据。
- CARD Target RMSE：Full `0.03137`，No_depth `0.03139`，No_residual `0.03163`；RCTD：`0.03096/0.03097/0.03114`。
- No_residual 较 Full 的 Target RMSE 变化：CARD +0.00026（约 +0.83%），RCTD +0.00018（约 +0.58%）。AUPRC：CARD 小幅下降，RCTD 小幅上升。均为模拟场景均值与五位小数精度，尚不构成统计显著/独立外部泛化证据。
- [RECORD] [三配置汇总](CARR-lite-V2/experiments/records/2026-11-21_three_config_ablation_summary.md)及 [六行 CSV 转录](CARR-lite-V2/experiments/records/2026-11-21_three_config_console_means.csv)。**原始输出仍仅在研究者本地，未独立复算。**
- [NEXT] `RCTD --ablation no_confusion_features --dry-run`；若检查通过则正式运行，随后 CARD。保留对照和负结果。

## 2026-11-21 CARD no_residual 已存在完整规模输出（最新）

- [USER_CONSOLE_DIR_CHECK] 用户运行 CARD no_residual 命令时被防覆盖检查拦截；本次**未重新训练**。随后只读检查目标目录，发现 52 子目录、`metrics_by_scenario.csv` 260 条记录和 `run_config.json`，修改时间均为 2026-11-21 18:48:48。
- [记录](CARR-lite-V2/experiments/records/2026-11-21_card_no_residual_existing_output.md)；这是已有文件的证据，随后用户已核对 run_config 字段为 `CARD/no_residual`，并读取指标汇总；但仍未上传原始 CSV。
- [NEXT] 一条只读命令验证 JSON 确认 `base_method=CARD`、`ablation=no_residual` 后，汇总 RCTD/CARD × Full/No-depth/No-residual 指标。

## 2026-11-21 RCTD no_residual 消融（最新用户终端）

- [RUN_LOG_CONFIRMED] `--method RCTD --ablation no_residual --dry-run`：52 场景检查通过，明确排除 `residual_projection` 与 `residual_marker_mean`。
- 用户正式运行日志：`FINISHED 260 result rows`，写入 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_residual`。
- [记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_residual_v1.md)。尚未收到指标 CSV，不能推断性能。
- [NEXT] CARD no_residual dry-run、正式运行，然后与 Full/No-depth 同口径比较。

## 2026-11-21 no_depth 均值对比（用户终端最新）

- [USER_CONSOLE_SUMMARY] HGBC_a30，各组 52 视图：CARD full `target_RMSE=0.03137`、no_depth `0.03139`；RCTD full `0.03096`、no_depth `0.03097`。
- AUPRC：CARD full `0.55561`、no_depth `0.55607`；RCTD full `0.55710`、no_depth `0.55681`。两种方法 recall@10%FPR 在 no_depth 下均略有增加。
- [RECORD] [均值报告](CARR-lite-V2/experiments/records/2026-11-21_no_depth_ablation_mean_results.md)及 [CSV](CARR-lite-V2/experiments/records/2026-11-21_no_depth_console_means.csv)。均值来自用户终端四舍五入数值，不等于原始结果已上传；尚不能声称统计等效。
- [NEXT] RCTD `--ablation no_residual --dry-run`；再视输入验证运行 RCTD/CARD 两组 no_residual。

## 2026-11-21 CARD no_depth 消融已完成（用户日志）

- [RUN_LOG_CONFIRMED] CARD `--ablation no_depth --dry-run` 输入检查 52 场景通过，明确排除 `depth_fraction` 特征。
- 正式执行日志末尾：`FINISHED 260 result rows`；输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_depth`。
- [记录](CARR-lite-V2/experiments/records/2026-11-21_card_no_depth_v1.md)。仍未读取原始性能 CSV，不推断 no_depth 影响方向。
- [NEXT] 从 RCTD/CARD full + no_depth 四份 `metrics_by_scenario.csv` 固定 `HGBC_a30` 输出同口径汇总，随后按 base 聚合描述。

## 2026-11-21 RCTD no_depth 消融已完成（用户日志）

- [RUN_LOG_CONFIRMED] RCTD `--ablation no_depth` dry-run 显示排除 `depth_fraction`，52 场景输入验证通过。
- 正式执行：终端 `FINISHED 260 result rows`，本地输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_depth`。
- [运行记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_depth_v1.md)。未收到实际指标 CSV，尚不能评价 no_depth 对性能的影响。
- [NEXT] CARD no_depth 已完成，继续同方法的 full vs no_depth 性能比较。

## 2026-11-21 CARR 按基础场景的配对比较（最新）

- [USER_CONSOLE_SUMMARY] 对 `HGBC_a30 - Original` 先按 `held_out_base` 对四种深度取均值；RCTD target_RMSE 改善 **13/13**、AUPRC 改善 **10/13**；CARD target_RMSE 改善 **13/13**、AUPRC 改善 **9/13**。
- [RECORD] [分组配对记录](CARR-lite-V2/experiments/records/2026-11-21_cross_method_by_base.md)。CARD 用户终端输出中 12 个逐组数值被截断，仅保存可信的汇总计数。
- [CODE_READY / NOT_RUN] 扩展了 CARR 跨方法脚本的 `--ablation` 选项，支持 no_depth/no_residual/no_confusion_features/no_marker_features。提交 `f5e3ead23bb122027a5c333d35021f283c2fddac`；新功能尚未本机运行。
- [NEXT] 本地 `git pull --ff-only` 获取更新，然后先跑 RCTD no_depth 输入检查。继续“先扩充，终期审计”的安排。

## 2026-11-21 CARR 跨方法汇总（最新用户控制台）

- [USER_CONSOLE_SUMMARY] 用户合并本地 RCTD/CARD `metrics_by_scenario.csv`，读取 520 行，按 `base_method, method` 取五指标均值并四舍五入到五位小数。
- RCTD：Original target_RMSE `0.05789`，HGBC_a15 `0.03089`（均值降幅按五位小数计算约 **46.64%**）。
- CARD：Original target_RMSE `0.03720`，HGBC_a30 `0.03137`（约 **15.67%**）。
- [LIMITATION] RCTD matrix_RMSE 原始 `0.08986`，a15/a30/a50 分别 `0.08999/0.09004/0.09011`，有轻微恶化；不同 a 的改变量不可后验当独立最优超参数结论。
- [RECORD] [均值报告](CARR-lite-V2/experiments/records/2026-11-21_cross_method_mean_results.md)及 [CSV 转录](CARR-lite-V2/experiments/records/2026-11-21_cross_method_console_means.csv)。只是用户控制台的汇总数据，**未独立读取本地原始 CSV**。
- [NEXT] 基础场景为单位汇总 4 个深度，观察 13 个场景各自的改善与失败情况；不启动额外全面审计。

## 2026-11-21 CARR CARD 扩充进度（用户终端日志）

- [RUN_LOG_CONFIRMED] CARD `--dry-run` 输入检查通过 52 个场景；正式运行终端显示 `FINISHED 260 result rows` 和 `OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\CARD`。
- [RECORD] [CARD 运行记录](CARR-lite-V2/experiments/records/2026-11-21_card_cross_method_v1.md)。
- [NEXT] 同时从用户 Windows 的 RCTD/CARD `metrics_by_scenario.csv` 汇总描述性性能表；暂不推断跨方法改善与独立显著性。

## 2026-11-21 CARR RCTD 扩充进度（用户终端日志）

- [RUN_LOG_CONFIRMED] `cross_method_carr_v2.py --method RCTD --dry-run` 输出 52 个场景全部通过输入检查；正式运行完成 52 个场景并显示 `FINISHED 260 result rows`。
- [LOCAL_OUTPUT] `D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\RCTD`；原始 `metrics_by_scenario.csv` 尚未读取，所以没有性能或显著性结论。
- [RECORD] [RCTD 运行记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_cross_method_v1.md)。
- [NEXT] CARD 跨基础方法的 dry-run 与正式执行；随后读取 RCTD + CARD 逐场景指标表。

## 2026-11-21 最新实验进度（用户终端日志）

- [RUN_LOG_CONFIRMED] CTW-RF `global_stacking_cv.py`：内存 selftest `SELFTEST PASS`；真实数据 dry-run 通过，2000 spot、19 细胞类型和六种基线。
- [RUN_LOG_CONFIRMED] 正式五折 GlobalStacking 运行完成，终端有 `WROTE`；结果：JSD `0.113543`，matrix_RMSE `0.048965`，aggregated_celltype_RMSE `0.867207`，mean_celltype_RMSE `0.045642`。这是用户提供的本地输出，非独立 CSV 复算。
- [RESULT_RECORD] [运行日志摘要及转录数值](CTW-RF/experiments/records/2026-11-21_global_stacking_v1.md)。原始结果在用户本地 `D:\Research\STdeconv_benchmark\results\CTWRF_GlobalStacking_20261121_v1`；尚未上传。
- [NEXT] 按执行优先安排 CARR CARD 跨方法实验 `--dry-run`（RCTD 已由用户日志确认完成）。前述 CTW 风险保留最终审计，不阻断扩充流程。

## 2026-11-21 最新决策：先执行扩充、终期集中审计

- [USER DECISION] 先按扩充计划推进两篇论文的新对照实验，**不再因每个潜在审计问题反复停工**；最终稿前集中审计。
- [RUN_LOG_CONFIRMED] CTW 实验脚本：[`global_stacking_cv.py`](CTW-RF/experiments/global_stacking_cv.py)，实现单方法、等权和全局非负 stacking 的同一五折比较；**已由用户日志确认本地运行成功，尚未收到原始 CSV**。
- [CODE_READY] CARR 实验脚本：[`cross_method_carr_v2.py`](CARR-lite-V2/experiments/cross_method_carr_v2.py)，支持 RCTD/CARD 基础方法的留出场景实验；**未运行**。
- [PLANNED] 先完成 CTW stacking 自检与本机输出，然后 CARR RCTD→CARD，后续才做更全面的消融、文献比较和终期审计。
- 操作队列与验收：[`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md)。
- 之前发现的风险仍保留在历史审计记录中，但不再作为每日新增的工作队列；最基本的无测试真值训练、记录完整和不覆盖输出仍需遵守。

## 2026-11-21 午间增量更新（已核实 GitHub）

- [GITHUB-VERIFIED] Codex 归档提交 `5666894905eb7e49d83158fbbcaf88e92ed8a03c`，**62 个文件**（CTW-RF 53、CARR-lite V2 9；Python 14、CSV 46、Markdown 2）。
- [VERIFIED-CODE] 已读 CTW 伪 spot 构造器、融合脚本、五折验证脚本与 CARR 两套特征/训练脚本；详见 [`SOURCE_AUDIT_2026-11-21.md`](SOURCE_AUDIT_2026-11-21.md)。
- [RISK] CTW 构造器将造伪 spot 所抽取的细胞所属**同一完整来源细胞集合**导出为参考文件，脚本未见划分；若基线实际使用此参考则构成细胞重用。下一步需要核实基线运行输入。
- [VERIFIED-CODE] CTW 的 spot 级五折权重学习使用每折训练部分；但在整份指标上选最佳 Proposed 版本，**仍无独立最终选型评价**。
- [VERIFIED-CODE] CARR 的 `depth_fraction` 在模拟中由已知深度标签直接构造；不应直接宣称真实未知深度可部署。
- [VERIFIED-CODE] CARR 脚本确有 leave-one-base-out 分组留出结构，但不同 base 之间是否共享源细胞/供体尚未验证。
- [UNVERIFIED] 归档只有部分脚本及历史汇总 CSV；**未取得原始输入、所有基础方法的真实预测和完整环境，未执行新实验或独立复算**。
- 本条属于历史审计建议；**当前执行优先级已由上方的最新决策替代**。

## 0. 证据状态约定

- **[VERIFIED-DOC]**：已直接读取对应文件，仅确认“文件中这样写”，不代表实验真实复算。
- **[GITHUB-VERIFIED]**：已从 GitHub API 读取/提交并核实。
- **[CLAUDE-REPORT / UNVERIFIED]**：来自用户转发的 Claude 审查文字，其所称本地文件、代码、实验不能视为本次已读取。
- **[PLANNED]**：准备执行，尚无运行结果。
- **[BLOCKED]**：缺少原始数据、脚本或权限。

## 1. 已确认的仓库状态

- [GITHUB-VERIFIED] GitHub 仓库已创建；README.md 和 AGENTS.md 已存在。
- [GITHUB-VERIFIED] AGENTS.md 初次提交：`798ea97426282f0cefd6f48628ad752252482b83`。
- [VERIFIED-DOC] 本次直接检查的上传稿件：
  - `CTW_RF_ICBBS2026_intro_reorganized.tex`，426 行，SHA-256 `802cf84f0de39bb843de467b1d7a03b252b96623e145142ed4f421b217ea51f7`。
  - `CARR-lite_V2_Method_Paper_Chinese(5).tex`，201 行，SHA-256 `8b079ccf0a47344d90cc5620615166534a51a42d3bd1164524a58f5002fff3fc`。
- **上述 LaTeX 只在本次对话附件中检查，尚未上传至公开仓库。**

## 2. 研究 A：CTW-RF

- 主张（稿件）：学习每种细胞类型的非负融合权重，融合多个基础反卷积器。
- [VERIFIED-DOC] 上传稿件描述 `cortex-SVZ-2000`：2,000 个伪 spot、19 类、五折评估；摘要报告 aggregate RMSE 0.724（CTW-RF）与 0.906（CARD），JSD 0.102（CTW-RF）与 0.099（cell2location）。**均是稿件报告，未独立复算。**
- [VERIFIED-DOC] DLPFC 151673 的 `0.298` 是由参考细胞生成的**伪 spot**上的 aggregate RMSE；真实 Visium 切片只有层标签支持定性/间接分析，不能声称已知真实细胞比例的预测误差。
- [CLAUDE-REPORT / UNVERIFIED] 可能存在伪 spot 构造与参考细胞重用；DLPFC 0.298 的训练/测试隔离脚本未定位；需比较 EnDecon 等接近工作的实现。
- **三项阻断风险**：① 参考/伪 spot 或权重训练/评估泄漏；② 与最近邻集成方法比较不足；③ 将伪 spot 定量结果与真实切片定性结果混淆。
- 下一步唯一优先动作：获取 CTW-RF 的伪 spot 构造脚本、融合/五折评估脚本、每折预测和真值 CSV，核实拆分链。
- 详细路线：[`CTW-RF/EXPERIMENT_PLAN.md`](CTW-RF/EXPERIMENT_PLAN.md)。

## 3. 研究 B：CARR-lite V2

- 主张（稿件）：在 Tangram 后建立残差修正、存在概率与阳性条件丰度三分支，组成约束后输出。
- [VERIFIED-DOC] 精简稿描述 13 个基础条件×4 深度 = 52 场景；seqFISH+ 5 个留出 FOV、合计 70 聚合 spot，26 类。
- [VERIFIED-DOC] 稿件报告半模拟 rare-positive RMSE 0.035965→0.016277；seqFISH+ singleton AUPRC 0.239072→0.334900、平均 spot JSD 0.426390→0.377208。**未核对原始日志或 CSV。**
- [VERIFIED-DOC] 文稿明确使用过“受控深度比例作为第 12 项特征”，这类实际部署可能未知的特征需要单独定义适用域/进行移除敏感性分析。
- [CLAUDE-REPORT / UNVERIFIED] Claude 称存在更完整 `CARRliteV2_Full_Manuscript_Chinese.tex`；**本次未收到该 Full 文件，不视为已审阅**。
- **三项阻断风险**：① 监督标签来源及 FOV/参考细胞隔离；② “即插即用模块”但只在 Tangram 上验证；③ 外部数据与真实部署特征不足。
- 下一步：取得实际模型训练与特征提取脚本、52 场景预测和五折 FOV 结果；先核实第 12 项特征和数据协议。
- 详细路线：[`CARR-lite-V2/EXPERIMENT_PLAN.md`](CARR-lite-V2/EXPERIMENT_PLAN.md)。

## 4. 跨项目约束与协同

- [PLANNED] **优先审计现有证据，再扩实验**，避免在原协议有问题时堆积结果。
- 可能共享统一的预测矩阵对齐、评估和日志模板，但两篇分别冻结协议与独立测试边界。
- [PLANNED] 探索“CTW-RF 融合输出 → CARR 校准输入”作为交叉场景；只有保证两层监督训练/测试无重叠、并提供基础方法与简单校准对照后才能作为正式实验。
- 不能把相同供体/切片/伪 spot、不同种子解释为多个独立生物学重复。
- 会议扩展投稿需先核实 CTW-RF 的正式发表/版权状况及目标期刊政策；“至少新增 30%”不是通用硬规则。

## 5. 当前待补资料（尚未取得）

1. 已归档部分源代码（commit 5666894）；**仍缺**完整环境、全部基础方法实际运行入口、运行记录；
2. 原始数据来源/许可、样本与参考细胞 ID、拆分清单、完整真值与预测矩阵、运行日志；
3. CTW-RF **已有部分历史汇总评估 CSV**；仍缺原始逐 spot 预测与 DLPFC 训练/测试分离证据；
4. CARR **已有部分历史 52 场景相关脚本及摘要表**；仍缺 Full 版稿件、52 场景/5 FOV 的完整原始逐样本证据；
5. 会议发表记录与扩展稿目标期刊要求。

## 6. 最新决定与交接

- [DECISION] 公开 GitHub 仅承载目前允许公开的规范/计划/审计文档；未经授权不公开上传的原始稿件、敏感数据或未经许可的外部资源。
- [DECISION] 本次**没有运行实验**、没有复算发表级指标、没有验证 Claude 所述 Windows 本地目录。
- 新对话请按顺序阅读 `AGENTS.md` → 本文件 → 最近 `RESEARCH_JOURNAL` → `EVIDENCE_REGISTER.md` → 对应实验计划。
- **下一步优先**：向研究者索取（或经授权读取）CTW-RF 伪 spot / 权重训练 / 评估脚本和对应 CSV，从数据泄漏审计开始。
