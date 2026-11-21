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
