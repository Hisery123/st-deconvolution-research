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
