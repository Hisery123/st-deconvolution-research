# 两篇 SCI 扩充：实验执行队列（2026-11-21）

> 当前决策：**优先按既定扩充清单交付新的可比较实验**。除非发现会直接导致错误运行/污染数据的阻断问题，暂不插入额外的全面审计任务；已有风险统一保留到最后的科研验收阶段。任何实验仍不得使用测试真值调参、伪造结果、覆盖历史记录。

## 当前状态

| 优先级 | 论文 | 实验 | 交付物 | 目前状态 |
|---|---|---|---|---|
| P1 | CTW-RF | 全局非负 stacking + 等权 + 原单方法 | `global_stacking_oof.csv`、`metrics_overall.csv`、`metrics_by_fold.csv`、`global_weights_by_fold.csv` | **用户日志确认运行成功；原始输出仍在本地** |
| P1 | CARR-lite V2 | RCTD + CARR 三分支（12 个 base 训练/1 个 base 留出） | 每场景预测 + `metrics_by_scenario.csv` | **用户日志确认 52 场景/260 条结果运行完成；待读取指标** |
| P2 | CARR-lite V2 | CARD + CARR 三分支 | 同上 | **脚本已提交；未运行** |
| P2 | CTW-RF | 更多随机划分、配对结果及图表 | CSV、SVG、配置与日志 | **计划** |
| P3 | CARR-lite V2 | 简单校准方法、特征消融和部署敏感性 | 公平对照 CSV | **计划** |
| P3 | CTW-RF | EnDecon 等最近邻集成基线及 DLPFC 应用扩展 | 可比较指标 | **计划；实现前需核对原文接口** |
| 终期 | 两篇 | 原始结果复核、泄漏/独立性审查、论文一致性与投稿政策 | 审计报告与正式论文表格 | **安排在扩充实验之后** |

## CARR RCTD 新增运行记录（2026-11-21）

- [RCTD 跨基础方法运行记录](CARR-lite-V2/experiments/records/2026-11-21_rctd_cross_method_v1.md)：用户先报告 RCTD 52 场景 `DRY RUN PASS`，后提供正式执行 `Completed` 至 B13 第四深度，末尾 `FINISHED 260 result rows`。
- 本地输出：`D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\RCTD`；**尚未独立读取 `metrics_by_scenario.csv`，不做性能提升声明**。
- **下一项：CARD 52 场景 dry-run → 正式执行；两项完成后做同口径指标汇总。**

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
