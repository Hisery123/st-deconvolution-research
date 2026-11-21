# CARR-lite V2 × RCTD：no_confusion_features 特征消融运行记录

- 日期：2026-11-21
- 证据等级：**RUN_LOG_CONFIRMED**（用户提供 Windows PowerShell 终端日志；尚未读取实验原始 CSV）
- 基础方法：RCTD。
- 方案：`--ablation no_confusion_features`，排除 `base_confusion_sum`、`base_target_minus_confmax`、`base_target_share_local`、`reference_similarity_max` 四个输入特征；其他校正机制仍保留，因此**不是整个混淆校正模块的消融**。
- 源脚本：[`../cross_method_carr_v2.py`](../cross_method_carr_v2.py)，消融实现提交 `f5e3ead23bb122027a5c333d35021f283c2fddac`。
- 本地输出：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_confusion_features`。

## 用户实际返回的检查日志

```text
INPUT CHECK PASS: RCTD 52 scenario views
ABLATION: no_confusion_features excluded columns: ['base_confusion_sum', 'base_target_minus_confmax', 'base_target_share_local', 'reference_similarity_max']
DRY RUN PASS — no files written
```

## 正式运行尾部日志

```text
Completed B12_lowref_ref70_depth_100
Completed B12_lowref_ref70_depth_050
Completed B12_lowref_ref70_depth_025
Completed B12_lowref_ref70_depth_010
Completed B13_lowref_bg8_depth_100
Completed B13_lowref_bg8_depth_050
Completed B13_lowref_bg8_depth_025
Completed B13_lowref_bg8_depth_010
FINISHED 260 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_confusion_features
```

## 当前解释与下一步

- 终端确认 RCTD 在 52 个场景上的该项消融完成、输出 260 行记录；**没有提供新的性能指标，不能推断优劣**。
- 52 个 scenario views 来自 13 组基础场景 × 4 个深度，不可写作 52 个独立生物学重复。
- 下一步按现有实验队列检查 `CARD --ablation no_confusion_features --dry-run`，通过后正式执行。再按固定 `HGBC_a30` 比较 Full、No_depth、No_residual、No_confusion_features。
