# CARR-lite V2 × RCTD/CARD：四配置（Full、No_depth、No_residual、No_confusion_features）消融均值

- 日期：2026-11-21
- **证据等级：USER_CONSOLE_SUMMARY**。用户在 Windows 端读取八份本地 `metrics_by_scenario.csv` 并粘贴 pandas `groupby.mean().round(5)` 的输出；仓库没有收到原始 260 行结果表，也未独立复算。
- 方案：固定 `HGBC_a30`，两种基础方法各四种特征配置，每一方法—配置 52 个场景视图（13 个基础场景 × 4 个测序深度），合计筛选记录数 416。四种测序深度不能当作四个生物学独立重复。
- 机器可读的控制台转录：[八行指标 CSV](2026-11-21_four_config_console_means.csv)。

## 完整终端汇总（保留用户打印的五位小数）

| base_method | variant | target_RMSE | target_MAE | balanced_AUPRC | recall_at_10pct_FPR | matrix_RMSE | n |
|---|---|---:|---:|---:|---:|---:|---:|
| CARD | Full | 0.03137 | 0.02380 | 0.55561 | 0.14690 | 0.09089 | 52 |
| CARD | No_confusion_features | 0.03110 | 0.02374 | 0.55432 | 0.14341 | 0.09090 | 52 |
| CARD | No_depth | 0.03139 | 0.02381 | 0.55607 | 0.14843 | 0.09089 | 52 |
| CARD | No_residual | 0.03163 | 0.02392 | 0.55421 | 0.14092 | 0.09089 | 52 |
| RCTD | Full | 0.03096 | 0.02375 | 0.55710 | 0.14184 | 0.09004 | 52 |
| RCTD | No_confusion_features | 0.03068 | 0.02364 | 0.55483 | 0.13750 | 0.09005 | 52 |
| RCTD | No_depth | 0.03097 | 0.02377 | 0.55681 | 0.14348 | 0.09004 | 52 |
| RCTD | No_residual | 0.03114 | 0.02383 | 0.55728 | 0.14181 | 0.09005 | 52 |

## no_confusion_features 相对 Full 的变化（由用户的五位小数均值计算）

| base_method | Δtarget_RMSE | Target RMSE 相对变化 | Δtarget_MAE | ΔAUPRC | Δrecall@10%FPR | Δmatrix_RMSE |
|---|---:|---:|---:|---:|---:|---:|
| CARD | -0.00027 | -0.86% | -0.00006 | -0.00129 | -0.00349 | +0.00001 |
| RCTD | -0.00028 | -0.90% | -0.00011 | -0.00227 | -0.00434 | +0.00001 |

## 当前证据支持的结论

- 在当前 52 视图的简单均值下，两种基础方法去掉**四个混淆输入特征**后目标 RMSE/MAE 都下降，意味着只看丰度估计会偏好该消融配置。
- 但同一消融使两基础方法的 AUPRC 与 Recall@10% FPR 均下降；**检测性能出现权衡**，不能声称 Full 在所有目标指标都最佳，也不能声称去混淆必然提高总体性能。
- No_depth 的平均 RMSE 变化很小；No_residual 的平均 Target RMSE 高于 Full；这些结果说明不同输入特征组对多个评价维度影响不同。
- 这只是特征消融而非完整机制消融；混淆约束和其他算法步骤仍存在。
- 没有外部测试、13 基础场景配对效应的区间估计或独立统计检验，**不可声明统计显著、真实平台可泛化或哪种配置普适最优**。

## 下一步（尚未运行）

- 完成最后一组 `no_marker_features`，首先 RCTD `--dry-run`，之后 RCTD/CARD 逐项正式运行，均保存到独立 `...\no_marker_features` 路径，不覆盖现有文件。
- 再使用所有结果按 `held_out_base` 聚合四种深度，制作完整消融对照图并如实保留负结果；暂不展开全面审计。
