# CARR-lite V2 × RCTD / CARD：10 组完整特征消融指标汇总

- 记录日期：2026-11-21
- **证据等级：USER_CONSOLE_SUMMARY**。用户在 Windows 端逐一读取本地 `metrics_by_scenario.csv`，筛选 `HGBC_a30`，粘贴 `groupby.mean().round(5)` 的 10 行结果。本仓库仅转录本轮用户终端数值；**原始 52 场景逐行结果未上传，无法在 GitHub 独立重算**。
- 设计：RCTD / CARD 两种基础方法 × Full、No_depth、No_residual、No_confusion_features、No_marker_features 五配置，各 52 视图（13 个 base × 每组 4 个 depth），`HGBC_a30` 共 520 条方法—配置—场景记录，**并非 520 个独立生物学重复**。
- 数值来源文件示例：`D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\RCTD\metrics_by_scenario.csv`；消融输出存于 `...\CARRliteV2_ablation_20261121_v1\{method}\{ablation}\metrics_by_scenario.csv`。
- [10 行终端数据 CSV](2026-11-21_five_config_console_means.csv) 保存全部五项指标和每组记录数量。

## 10 组实际均值（控制台显示的 5 位小数）

| base_method | variant | target_RMSE | target_MAE | balanced_AUPRC | recall_at_10pct_FPR | matrix_RMSE |
|---|---|---:|---:|---:|---:|---:|
| CARD | Full | 0.03137 | 0.02380 | 0.55561 | 0.14690 | 0.09089 |
| CARD | No_confusion_features | 0.03110 | 0.02374 | 0.55432 | 0.14341 | 0.09090 |
| CARD | No_depth | 0.03139 | 0.02381 | 0.55607 | 0.14843 | 0.09089 |
| CARD | No_marker_features | 0.03137 | 0.02380 | 0.55645 | 0.14954 | 0.09090 |
| CARD | No_residual | 0.03163 | 0.02392 | 0.55421 | 0.14092 | 0.09089 |
| RCTD | Full | 0.03096 | 0.02375 | 0.55710 | 0.14184 | 0.09004 |
| RCTD | No_confusion_features | 0.03068 | 0.02364 | 0.55483 | 0.13750 | 0.09005 |
| RCTD | No_depth | 0.03097 | 0.02377 | 0.55681 | 0.14348 | 0.09004 |
| RCTD | No_marker_features | 0.03106 | 0.02384 | 0.55755 | 0.14017 | 0.09004 |
| RCTD | No_residual | 0.03114 | 0.02383 | 0.55728 | 0.14181 | 0.09005 |

## 新增 No-marker 对比（No_marker − Full）

| base_method | Δtarget_RMSE | Δtarget_MAE | ΔAUPRC | Δrecall@10%FPR | Δmatrix_RMSE |
|---|---:|---:|---:|---:|---:|
| CARD | 0.00000 | 0.00000 | +0.00084 | +0.00264 | +0.00001 |
| RCTD | +0.00010 | +0.00009 | +0.00045 | −0.00167 | 0.00000 |

- CARD 的目标 RMSE 和 MAE 在**输出精度下**相同，不可证明原始数值完全相等。
- RCTD 去掉 marker 输入特征后目标 RMSE 上升约 `0.00010 / 0.03096 = 0.32%`；AUPRC 略增，而固定 FPR 召回率略降。CARD 的 AUPRC 与召回都略增。
- 没有证据支持 marker 三个输入特征在两种基础方法所有指标都一致提升。该实验只是**输入特征消融**，没有移除整个 marker gene 相关流程。
- 汇总四种特征消融：No_depth 在均值上变化很小；No_residual 在两种方法的目标 RMSE 上升；No_confusion_features 在两种方法的目标 RMSE 下降但 AUPRC/Recall 均下降；No_marker 的影响较小且方向不同。
- 本轮结果不能主张“统计等效”“显著提升”或“外部泛化”；均值可能掩盖 13 个基础场景间的差异。完整结果要按 base 聚合四种深度，再报告配对差值和不确定性。

## 建议论文结果段落（中文证据草稿）

> 在 13 组基础模拟场景与 4 档测序深度形成的 52 个场景视图中，我们对 RCTD 与 CARD 两种基础反卷积方法进行了 CARR-lite V2 后校准和预设特征组消融。固定 HGBC_a30 设置后，去除深度特征对整体平均性能影响较小，而去除残差相关输入特征使两种基础方法的平均目标细胞 RMSE 略微上升。去除混淆相关输入特征降低了两方法的目标细胞 RMSE，但同时降低了 balanced AUPRC 和固定 10% 误报率下的召回率，反映出丰度误差与存在性检测之间的权衡。去除 marker 特征对结果影响较小、方向并不一致：CARD 的目标细胞 RMSE 在五位小数精度下没有变化，而 RCTD 的目标细胞 RMSE 略增。以上结论仅对应当前模拟体系中的描述性汇总，仍需基于基础场景进行配对核查。

## 下一项数据整理（尚未执行）

- 使用本地原始十份 CSV，以 13 个 `held_out_base` 为分组单位，对四个深度取均值，计算四种消融相对 Full 的配对改变量、改善场景数量和所有指标的结果表。
- 制作可以复用的 Matplotlib 可编辑矢量（SVG）绘图脚本并附数据表；保留负结果与 trade-off，不在图中冒充独立生物学重复。
- 结束本轮第二篇特征消融后，按照既定计划推进第一篇 CTW-RF 补充实验，或者根据现有证据安排真正独立的数据验证；不开展无关的新模型探索。
