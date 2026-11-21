# CARR-lite V2：104 行按 base 配对绘图数据导出成功（用户日志）

- 记录日期：2026-11-22（文件名沿用实验批次后缀 20261121）。
- **证据等级：USER_CONSOLE_EXPORT_LOG**。用户在 Windows PowerShell 端执行 pandas 导出后，返回确切终端输出：
  ```text
  WROTE D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_base_paired_20261121_v1.csv ROWS 104
  ```
- 这是**本地 CSV 生成成功**的日志，**不是** CSV 已上传至 GitHub，亦不代表 assistant 已直接读取、核验 104 行原始数值。
- 本地文件：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_base_paired_20261121_v1.csv`。
- 生成设计：RCTD / CARD 两种基础方法，四项特征消融 `no_depth`、`no_residual`、`no_confusion_features`、`no_marker_features`，13 组 `held_out_base`，共 2×4×13 = 104 条配对结果。
- 对每个基础场景，先在固定 `HGBC_a30` 变体下对 4 个深度取均值，再对消融和 Full 取配对差值。
- 含五项指标：`target_RMSE`、`target_MAE`、`balanced_AUPRC`、`recall_at_10pct_FPR`、`matrix_RMSE`。导出程序要求每组 13 个不同 held_out_base、总数 104、拒绝覆盖目标文件。
- 上一轮导出命令使用 `validate='one_to_one'` 报 `MergeError`；已修正为 `validate='many_to_one'` 后导出成功。不涉及重训或旧结果覆盖。

## 下一步

请研究者**上传该精确本地 CSV 到当前对话**，供助手直接核验列名、配对关系、缺失值及计算效应量，然后编写可编辑 SVG 绘图脚本与论文 Results 素材。未收到 CSV 前不能绘制以其详细数据为基础的真实数据点图，更不能编造逐 base 数值。
