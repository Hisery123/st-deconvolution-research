# 2026-11-22 RCTD 简单后校准对照正式运行日志

## 证据状态

- **USER_WINDOWS_STDOUT / RUN_COMPLETED_AS_REPORTED**：研究者在 Windows PowerShell 执行 RCTD 简单校准基线脚本并返回日志尾部。
- RCTD 的 Dry-run 此前通过 52 视图、13 个基础场景、四类别留出检查。
- 本轮正式实验目标：在与 CARR 严格四类别留出相同的划分上，评价原始 RCTD 以及两个预先固定的简单校准基线：`Ridge12` 与 `Isotonic1D`。
- **仅确认正式程序输出已完成；原始 `metrics_by_scenario.csv` 尚未直接读取，未报告任何方法性能比较、统计显著性或真实数据外部泛化。**

## 本次用户提供的原始终端尾部

```text
Completed B12_lowref_ref70_depth_100
Completed B12_lowref_ref70_depth_050
Completed B12_lowref_ref70_depth_025
Completed B12_lowref_ref70_depth_010
Completed B13_lowref_bg8_depth_100
Completed B13_lowref_bg8_depth_050
Completed B13_lowref_bg8_depth_025
Completed B13_lowref_bg8_depth_010
FINISHED 156 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\RCTD
```

## 程序及本地输出

- GitHub 脚本：[`simple_calibration_category_holdout.py`](../simple_calibration_category_holdout.py)；首次提交 `2b198ecbfdab0a4eba0827ba8ed07c88ed62a67d`。
- 用户本地运行命令（此前单独提供）：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\simple_calibration_category_holdout.py" --method RCTD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1"
```

- 本地输出：`D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\RCTD\metrics_by_scenario.csv`；156 行是52模拟视图×3个标签，不是156独立生物重复。

## 下一步（唯一手动操作）

先执行 CARD 简单对照输入检查，不直接正式运行：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\simple_calibration_category_holdout.py" --method CARD --dry-run
```

预期：`INPUT CHECK PASS: CARD 52 scenario views / 13 bases`、`SPLIT CHECK PASS: four disjoint held-out categories`、`CONTROLS: Ridge12, Isotonic1D`、`DRY RUN PASS — no files written`。错误时返回完整日志，不强制覆盖/删除已有结果。通过后再单独执行 CARD 正式实验，最后统一读取RCTD/CARD指标并与同协议CARR的`HGBC_a30`比较。
