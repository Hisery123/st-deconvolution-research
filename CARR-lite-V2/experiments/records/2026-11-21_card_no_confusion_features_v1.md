# CARR-lite V2 × CARD：no_confusion_features 特征消融运行记录

- 日期：2026-11-21
- 证据等级：**RUN_LOG_CONFIRMED**（用户提供 Windows PowerShell 终端日志；尚未读取实验原始 CSV）
- 基础方法：CARD。
- 方案：`--ablation no_confusion_features`，排除 `base_confusion_sum`、`base_target_minus_confmax`、`base_target_share_local`、`reference_similarity_max` 四个输入特征；**其他局部混淆修正机制仍在，不能称整体模块消融**。
- 源脚本：[`../cross_method_carr_v2.py`](../cross_method_carr_v2.py)，消融功能的引入提交 `f5e3ead23bb122027a5c333d35021f283c2fddac`。
- 本地输出目录：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_confusion_features`。

## Dry-run（用户此前返回）

```text
INPUT CHECK PASS: CARD 52 scenario views
ABLATION: no_confusion_features excluded columns: ['base_confusion_sum', 'base_target_minus_confmax', 'base_target_share_local', 'reference_similarity_max']
DRY RUN PASS — no files written
```

## 正式运行（用户此轮返回）

```text
Completed B12_lowref_ref70_depth_050
Completed B12_lowref_ref70_depth_025
Completed B12_lowref_ref70_depth_010
Completed B13_lowref_bg8_depth_100
Completed B13_lowref_bg8_depth_050
Completed B13_lowref_bg8_depth_025
Completed B13_lowref_bg8_depth_010
FINISHED 260 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_confusion_features
```

## 下一步与解释边界

- 用户日志确认 CARD 的 52 场景消融运行结束、输出 260 条记录；不包含性能指标数值，尚不能判定性能收益或损失。
- RCTD 与 CARD 两方法的 Full、no_depth、no_residual、no_confusion_features 共八组已经有执行成功/既有配置验证证据。
- [RCTD 同项消融记录](2026-11-21_rctd_no_confusion_features_v1.md)。
- 下一步用用户 Windows 本地的八份 `metrics_by_scenario.csv` 按固定 `HGBC_a30` 读取五项均值，各组应为 52 条指标记录。不要把 52 场景误作 52 个独立生物学重复，也不覆盖此前文件。
