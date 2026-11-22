# CARR-lite V2：同一模拟视图下严格类别留出 vs 逐 base 留出（2026-11-22）

## 证据与当前状态

- [USER_WINDOWS_STDOUT] 用户在 Windows PowerShell 将原 `CARRliteV2_cross_method_20261121_v1` 与严格类别留出 `CARRliteV2_category_holdout_20261122_v1` 中 RCTD/CARD 的 `HGBC_a30` 按 `base_method, scenario_id, held_out_base` 进行 `one_to_one` 配对；按每个 `held_out_base` 平均四档测序深度后计算 `strict-old`。
- 日志：`PAIR CHECK PASS: 104 views, 26 method-base pairs`，等于每法 52 视图、13 base，总计26个*方法×base*单元。
- **结论仅基于用户控制台输出的描述性汇总**；尚未得到新旧两批原始 52-view CSV，不能逐行独立复算或进行独立生物重复显著性推断。

## 严格类别留出比逐 base 留出更差的 base 数

| 基础方法 | 目标 RMSE 严格划分更差（strict > old） | Balanced AUPRC 严格划分更差（strict < old） |
|---|---:|---:|
| CARD | **13/13** | **13/13** |
| RCTD | **13/13** | **7/13** |

## 按类别的平均成对差值（严格 − 旧）

| 基础方法 | 场景类别 | Δ target_RMSE | Δ balanced_AUPRC |
|---|---|---:|---:|
| CARD | confusable | +0.000800 | −0.009385 |
| CARD | lowref | +0.000627 | −0.007518 |
| CARD | medium | +0.003619 | −0.008322 |
| CARD | stable | +0.001417 | −0.014906 |
| RCTD | confusable | +0.001408 | −0.004533 |
| RCTD | lowref | +0.000576 | +0.000480 |
| RCTD | medium | +0.002350 | −0.013701 |
| RCTD | stable | +0.001273 | +0.010365 |

**注意：** “严格类别留出”是在相同52个受控模拟视图上换分割策略、另行重训校准器，底层 Original 预测并未改变；该敏感性实验证明在更难拆分下 CARR 相对旧协议更脆弱，但不能据此证明外部真实组织上也会同幅下降。RCTD 在 stable 的检测AUPRC改善、CARD 在 stable 的AUPRC下降；不允许只报告有利类别。

## 结合此前严格类别留出与 Original 对比

- CARD `HGBC_a30` vs `Original_CARD`：Target RMSE `0.03720→0.03297`（较低），Balanced AUPRC `0.55189→0.54521`（反而下降），Recall@10%FPR `0.14612→0.13832`（反而下降）。
- RCTD `HGBC_a30` vs `Original_RCTD`：Target RMSE `0.05789→0.03236`、Balanced AUPRC `0.54487→0.55619`、Recall `0.12454→0.14103`；但 Matrix RMSE `0.08986→0.09012`（略恶化）。

## 决策与下个任务

- Claude 原计划第4项“严格类别留出”的运行、汇总、配对诊断已完成（终端证据）。
- **下一项：原计划第6项“简单后校准基线”**。同样在四类别留出折上训练/测试简单校准器（如一维 isotonic 和全特征线性 Ridge），与同协议 `Original`、`AbundanceOnly` 和 `HGBC_a30` 公平比较，预先固定模型与超参，不根据测试结果挑优。
- 后续还需要独立真实数据验证、FOV 等级统计及最终证据审计；不可因为实验工作量大就称创新已被证明。
