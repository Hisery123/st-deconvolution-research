# CARR-lite V2 × RCTD：no_residual 特征消融运行记录

- 日期：2026-11-21
- 证据等级：**RUN_LOG_CONFIRMED**（用户提供 Windows PowerShell 控制台输出；尚未读取本地原始 CSV）
- 基础方法：RCTD
- 配置：`--ablation no_residual`，从模型输入移除 `residual_projection` 和 `residual_marker_mean` 两列
- 脚本：[`../cross_method_carr_v2.py`](../cross_method_carr_v2.py)，可选消融功能由提交 `f5e3ead23bb122027a5c333d35021f283c2fddac` 引入
- 本地结果目录：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_residual`
- 实验设计：13 个 held-out base × 4 个 depth 场景；结果包含每个场景多个变体共 260 行。场景不等于独立生物学重复。

## 本次用户提供的输入检查日志

```text
INPUT CHECK PASS: RCTD 52 scenario views
ABLATION: no_residual excluded columns: ['residual_projection', 'residual_marker_mean']
DRY RUN PASS — no files written
```

## 正式运行完成标记（用户终端）

```text
Completed B11_lowref_ref50_depth_010
Completed B12_lowref_ref70_depth_100
Completed B12_lowref_ref70_depth_050
Completed B12_lowref_ref70_depth_025
Completed B12_lowref_ref70_depth_010
Completed B13_lowref_bg8_depth_100
Completed B13_lowref_bg8_depth_050
Completed B13_lowref_bg8_depth_025
Completed B13_lowref_bg8_depth_010
FINISHED 260 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_residual
```

## 结果边界和下一步

- 该日志确认用户本机完成了 RCTD/no_residual 实验，并**不**表明消融后性能下降或提升。
- 仅属于输入特征组消融，不能声称删除整个残差修正模块。
- 后续先跑 CARD/no_residual `--dry-run`，再执行 CARD 消融；固定 `HGBC_a30` 汇总 RCTD、CARD 的 full、no_depth、no_residual。
- 不覆盖既有结果；正式分析需要读取 `metrics_by_scenario.csv`。
