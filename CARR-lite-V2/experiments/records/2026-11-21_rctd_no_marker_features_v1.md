# CARR-lite V2 × RCTD：no_marker_features 特征消融运行记录

- 日期：2026-11-21
- 证据等级：**RUN_LOG_CONFIRMED**（用户 Windows PowerShell 日志，未直接读取原始 CSV）
- 方法：RCTD；配置 `--ablation no_marker_features`。
- 排除输入特征：`observed_marker_score`、`observed_marker_margin`、`marker_fit_target`；属于标记基因输入特征消融，**不是完整 marker 模块消融**。
- 脚本：[cross_method_carr_v2.py](../cross_method_carr_v2.py)，特征消融功能引入提交 `f5e3ead23bb122027a5c333d35021f283c2fddac`。
- 本地输出：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_marker_features`。

## 用户先前返回的输入验证

```text
INPUT CHECK PASS: RCTD 52 scenario views
ABLATION: no_marker_features excluded columns: ['observed_marker_score', 'observed_marker_margin', 'marker_fit_target']
DRY RUN PASS — no files written
```

## 用户本轮正式执行末尾

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
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_marker_features
```

## 解释边界与下一步

- 日志确认 52 场景输出、260 条场景—变体记录；原始指标 `metrics_by_scenario.csv` 尚未上传/读取，**不能推断特征消融的性能变化**。
- 同一基础场景的四个深度不是四次独立生物学重复。
- RCTD 现在已经完成 Full、No_depth、No_residual、No_confusion_features、No_marker_features 共五配置；下一步先做 CARD `--ablation no_marker_features --dry-run`，通过后正式运行 CARD。
- CARD 同组完成后统一比较两种方法×五配置，固定 `HGBC_a30`；保留结果不覆盖，不进行全面审计。
