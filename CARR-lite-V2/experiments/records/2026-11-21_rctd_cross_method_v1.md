# CARR-lite V2 × RCTD：52 场景跨基础方法实验记录

- 日期：2026-11-21（用户提供的 Windows PowerShell 终端日志）
- 状态：**RUN_LOG_CONFIRMED**（用户日志确认完成；原始 metrics CSV 尚未上传或复核）
- 方法：RCTD 基础预测 + 按基础场景留出的 CARR-lite V2 校准
- 实验脚本：[cross_method_carr_v2.py](../cross_method_carr_v2.py)，首次提交 `4583fa605bd175779c91a4ba665a0d6dcc1fd7d2`
- 本地环境提示符：`(.venv) (ST_Clustering)`（具体包版本未核实）
- 本地输出路径：`D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\RCTD`

## 用户实际运行的步骤

- [RUN_LOG_CONFIRMED] `python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\cross_method_carr_v2.py" --method RCTD --dry-run`
- 终端：`INPUT CHECK PASS: RCTD 52 scenario views` 和 `DRY RUN PASS — no files written`。
- [RUN_LOG_CONFIRMED] 使用 `--method RCTD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1"` 正式执行。
- 用户粘贴的后半段日志显示 `Loaded 52 / 52 B13_lowref_bg8_depth_010`；从 B01 到 B13 的每个基础场景四种深度均显示 `Completed`。
- 终端末尾：

```text
FINISHED 260 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_cross_method_20261121_v1\RCTD
```

## 本次运行可确认的边界

- `260 = 52 × 5`，按脚本结构对应原始 RCTD、仅丰度修正、HGBC_a15、HGBC_a30、HGBC_a50。
- 代码使用完整 base 留出作为训练/测试分组；用户尚未提供生成的逐场景预测及 `metrics_by_scenario.csv`，因此**不能填写性能改善百分比、统计显著性或泛化结论**。
- 本次未改动历史的 Tangram/CARR 源脚本；新适配脚本的运行结果保留在独立输出目录。
- 后续计划：先对 CARD 执行只读 `--dry-run`，通过后再正式运行；随后将 RCTD、CARD、Tangram 的同口径指标整理到论文对照表。

## 原始证据待归档

- `RCTD/metrics_by_scenario.csv`
- `RCTD/run_config.json`
- 预测输出（可选择性归档小文件，遵守公开仓库的数据许可）
- 完整终端日志和实际执行 Python/包版本

没有收到上述原始证据前，本记录只表示**用户提供的运行日志确认完成**，不是实验结果独立复算。
