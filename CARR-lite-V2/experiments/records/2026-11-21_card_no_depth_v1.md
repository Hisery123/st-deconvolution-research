# CARR-lite V2 × CARD — no_depth 特征消融运行记录

- 日期：2026-11-21
- 来源：用户 PowerShell 终端日志
- 状态：**RUN_LOG_CONFIRMED**，仅确认运行完成，未收到原始指标 CSV
- 脚本：[`../cross_method_carr_v2.py`](../cross_method_carr_v2.py)（消融选项由提交 `f5e3ead23bb122027a5c333d35021f283c2fddac` 增加）
- 输入：CARD 在 13 个基础场景 × 4 种测序深度的 52 视图预测
- 消融：`--ablation no_depth`，去掉 `depth_fraction` 输入特征
- 本地输出：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_depth`

## 用户已返回的实验日志

只读输入检查：

```text
INPUT CHECK PASS: CARD 52 scenario views
ABLATION: no_depth excluded columns: ['depth_fraction']
DRY RUN PASS — no files written
```

正式执行末尾：

```text
Completed B12_lowref_ref70_depth_050
Completed B12_lowref_ref70_depth_025
Completed B12_lowref_ref70_depth_010
Completed B13_lowref_bg8_depth_100
Completed B13_lowref_bg8_depth_050
Completed B13_lowref_bg8_depth_025
Completed B13_lowref_bg8_depth_010
FINISHED 260 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_depth
```

## 下一步与证据边界

- 与 [RCTD no_depth 运行记录](2026-11-21_rctd_no_depth_v1.md)一起，完成两种方法的第一组消融执行。
- 原始本地 `metrics_by_scenario.csv` 尚未读取/上传，**不能声称去除深度特征后性能下降、上升或无差异**。
- 先从每个基础方法各自的 full 与 no_depth 输出读取相同 `HGBC_a30` 变体，统一汇总 `target_RMSE`、`target_MAE`、`balanced_AUPRC`、`recall_at_10pct_FPR`、`matrix_RMSE`；如需论文统计，再按 13 个 held-out-base 聚合、保留四深度成组结构。
- 不使用 `--force`，不覆盖原始 RCTD/CARD 输出，不把技术场景误称为独立生物重复。
