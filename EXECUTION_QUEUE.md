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
