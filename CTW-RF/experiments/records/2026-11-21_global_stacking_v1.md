# CTW-RF Global Stacking — 扩充实验 01

- 日期：2026-11-21（用户 PowerShell 日志）
- 来源：研究者在本次对话粘贴的实际终端输出（非 AI 自行运行）
- 结果等级：**RUN_LOG_CONFIRMED / 原始输出 CSV 尚未提交或独立读取**
- 脚本：[`../global_stacking_cv.py`](../global_stacking_cv.py)
- 脚本提交：`7124f21fa5960e59a0613aff505c63c64bfbcc8c`
- 命令：

```powershell
python "D:\Research\st-deconvolution-research\CTW-RF\experiments\global_stacking_cv.py" --base-dir "D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots" --out-dir "D:\Research\STdeconv_benchmark\results\CTWRF_GlobalStacking_20261121_v1"
```

## 日志状态与输入

1. `--selftest`：终端显示 `SELFTEST PASS`。
2. `--dry-run`：终端显示 `Inputs ready: 2000 spots, 19 cell types; methods: Tangram, RCTD, CellDART, CARD, cell2location, SPOTlight`；`DRY RUN PASS (no files written)`。
3. 正式运行：终端打印 8 个方法的指标表，并返回 `WROTE D:\Research\STdeconv_benchmark\results\CTWRF_GlobalStacking_20261121_v1`。
4. 该输出目录中的实际五折 CSV、预测矩阵和 JSON **尚未上传/读取**，本记录的数值均为用户终端输出转录。

## Console metrics（原样精度）

| method | JSD | matrix_RMSE | aggregated_celltype_RMSE | mean_celltype_RMSE |
|---|---:|---:|---:|---:|
| Tangram | 0.317789 | 0.100129 | 1.662700 | 0.087511 |
| RCTD | 0.242249 | 0.075485 | 1.369653 | 0.072087 |
| CellDART | 0.345019 | 0.123992 | 2.124436 | 0.111812 |
| CARD | 0.124731 | 0.053021 | 0.906429 | 0.047707 |
| cell2location | 0.098996 | 0.056752 | 0.989714 | 0.052090 |
| SPOTlight | 0.312137 | 0.079721 | 1.488685 | 0.078352 |
| EqualWeight | 0.160047 | 0.058340 | 1.089242 | 0.057329 |
| GlobalStacking | 0.113543 | 0.048965 | 0.867207 | 0.045642 |

## 初步解读（仅此半模拟数据）

- GlobalStacking 在两个 RMSE 指标优于 EqualWeight 和六个单方法；JSD `0.113543` 仍高于 cell2location 的 `0.098996`。
- GitHub 历史 `source-snapshot/evaluation & visualization/reliability_fusion_2000spots_cv_verify/03_main_cv_comparison.csv` 中 `Proposed_CV` 为 JSD `0.1017517246`、matrix RMSE `0.0414667231`、aggregated RMSE `0.7256698232`。与本次 GlobalStacking 的打印数字对照，CTW Proposed_CV 较低；**其实现/折划分/选型规则尚未核对到可以声明正式配对优势的程度**。
- 需要最终比较时使用相同的预定义五折索引、相同独立样本、配对统计，并核对训练/测试边界。本轮不将这些终期审计工作插入实验执行队列。

## 预计本地原始输出（未收到文件）

```text
D:\Research\STdeconv_benchmark\results\CTWRF_GlobalStacking_20261121_v1\
  metrics_overall.csv
  metrics_by_fold.csv
  global_weights_by_fold.csv
  global_stacking_oof.csv
  run_config.json
```

当前结论：**首项扩充实验本地运行成功（由用户日志确认）**；复算/独立外部验证、正式统计结论仍为未完成。
