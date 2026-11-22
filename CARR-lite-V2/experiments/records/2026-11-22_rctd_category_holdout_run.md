# 2026-11-22 CARR-lite V2 严格类别留出：RCTD 正式运行完成（用户日志）

## 证据等级与实验状态

- **证据类型：USER_WINDOWS_STDOUT**
- **执行状态：RUN_COMPLETED_AS_REPORTED**，依据研究者 PowerShell 尾部日志，不代表助手已取得或重算原始结果 CSV。
- 方法：`RCTD`
- 代码：`CARR-lite-V2/experiments/category_holdout_carr_v2.py`，脚本首次提交 `4da4c29076c757467d7704a151fca40c64c5fc13`。
- 协议：四折 `stable/medium/confusable/lowref` 整类留出，13 个基础场景 ×4 深度共 52 视图；每法有 `Original_RCTD`、`AbundanceOnly`、`HGBC_a15`、`HGBC_a30`、`HGBC_a50` 五种评估输出。不得将52视图视为52个独立生物学重复。
- 运行命令（前一轮已给出，用户尾部输出表示已执行）：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\category_holdout_carr_v2.py" --method RCTD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1"
```

## 研究者返回的日志尾部

```text
Completed B12_lowref_ref70_depth_050
Completed B12_lowref_ref70_depth_025
Completed B12_lowref_ref70_depth_010
Completed B13_lowref_bg8_depth_100
Completed B13_lowref_bg8_depth_050
Completed B13_lowref_bg8_depth_025
Completed B13_lowref_bg8_depth_010
FINISHED 260 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\RCTD
```

## 证据边界与后续

- 上一轮 `--dry-run` 已由研究者终端确认 `INPUT CHECK PASS: RCTD 52 scenario views / 13 bases` 及四折测试规模（16/12/12/12）。
- 当前确认成功完成 260 行写出；尚未取得 `metrics_by_scenario.csv` 或执行数值比较，**不可宣称性能改善或外部泛化**。
- **下一步唯一人工操作**：`CARD` 严格类别留出 `--dry-run`，验证同一 52 场景和四类别划分，成功后再正式运行 CARD。切勿覆盖 RCTD 输出。
