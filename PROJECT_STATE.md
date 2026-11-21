# PROJECT_STATE — CTW-RF × CARR-lite V2

- 更新：2026-11-21（Asia/Taipei）
- 阶段：**CARR RCTD no_depth 特征消融已有用户成功运行日志；准备 CARD no_depth**
- 当前仓库：`Hisery123/st-deconvolution-research`（公开，main）
- 注意：本文件只记录已检查的稿件内容和明确的待办；**论文数字尚未用原始 CSV/代码独立复算**。不得将文中叙述等同于已复现实验。

## 2026-11-21 RCTD no_depth 消融已完成（用户日志）

- [RUN_LOG_CONFIRMED] RCTD `--ablation no_depth` dry-run 显示排除 `depth_fraction`，52 场景输入验证通过。
- 正式执行：终端 `FINISHED 260 result rows`，本地输出 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_depth`。
- [运行记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_no_depth_v1.md)。未收到实际指标 CSV，尚不能评价 no_depth 对性能的影响。
- [NEXT] CARD no_depth dry-run 和正式运行，之后再进行同方法配对性能对比。

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
