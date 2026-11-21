# CARR-lite V2：五配置消融的基础场景改善计数

- 日期：2026-11-21
- **证据等级：USER_CONSOLE_SUMMARY**；研究者通过 PowerShell 的 pandas 命令，直接读取本地 RCTD/CARD 的 Full 及四种输入特征消融结果；GitHub 目前只有终端汇总，未持有按场景的完整 CSV。
- 分析单位：13 个 `held_out_base` 基础场景，每个基础场景内先对 4 个 depth 的 `HGBC_a30` 指标取均值。
- 差值方向：消融 − Full；`rmse_improved = target_RMSE_ablation < target_RMSE_full`；`auprc_improved = balanced_AUPRC_ablation > balanced_AUPRC_full`。严格不等号，因此其余数量只是“未改善”，**可能包含持平，不自动归为恶化**。
- 基础场景计数：所有基础方法×消融组合的 `held_out_base` 唯一值均为 **13**。
- 本次数据来源是用户终端粘贴的实际执行输出，不是独立复算。

## 完整用户终端计数

| base_method | variant | rmse_improved (of 13) | auprc_improved (of 13) |
|---|---|---:|---:|
| CARD | no_confusion_features | 6 | 7 |
| CARD | no_depth | 6 | 7 |
| CARD | no_marker_features | 6 | 7 |
| CARD | no_residual | 4 | 5 |
| RCTD | no_confusion_features | 7 | 6 |
| RCTD | no_depth | 5 | 4 |
| RCTD | no_marker_features | 2 | 6 |
| RCTD | no_residual | 5 | 6 |

## 对照已有 52 场景均值的解释（不新增实验数字）

参考此前 [十组特征消融均值表](2026-11-21_five_config_ablation_summary.md)：

- 在 RCTD `no_marker_features` 组，只有 2/13 个 base 的 Target RMSE 比 Full 低；整体平均 Target RMSE 却稍高（0.03096 → 0.03106）。不能据计数推断其余 11 组均严格恶化或存在统计显著性。
- CARD `no_residual` 仅 4/13 组 Target RMSE 改善；52 视图平均 Target RMSE `0.03137 → 0.03163`。
- `no_confusion_features` 的 52 视图平均 Target RMSE 对两基础方法均降低，然而改善计数分别是 CARD 6/13、RCTD 7/13；同时均值 AUPRC 和 Recall 在两方法均下降。存在效应大小不均衡以及丰度估计与检测之间的权衡。
- `no_depth` 的 52 视图均值变化较小，逐 base 效应方向并非全都一致。
- 本计数是描述性敏感性结果；13 个 base 来自同一模拟套件，不是独立供体的重复。

## 下一步数据整理

需从用户本地十份 `metrics_by_scenario.csv` 导出按 `held_out_base` 聚合四深度的逐 base 原值与消融−Full 配对差值（应产生 RCTD/CARD × 4 个消融 × 13 个 base = **104 行配对差值**）；存到一个新增 CSV。此项未执行、未产生文件。

之后再设计具有可编辑 SVG 输出的科研图；不制造模拟结果、显著性或任何未经验证的 SCI 结论。
