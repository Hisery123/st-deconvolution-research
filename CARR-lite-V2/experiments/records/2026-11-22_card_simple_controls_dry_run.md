# 2026-11-22 CARD 简单校准基线 Dry-run 通过

- 证据等级：**USER_WINDOWS_STDOUT**，仅核实输入检查通过，不代表拟合完成或指标已获得。
- 用户执行的完整命令：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\simple_calibration_category_holdout.py" --method CARD --dry-run
```

- 用户终端原样输出：

```text
FOLD stable train_views 36 test_views 16 test_bases 4
FOLD medium train_views 40 test_views 12 test_bases 3
FOLD confusable train_views 40 test_views 12 test_bases 3
FOLD lowref train_views 40 test_views 12 test_bases 3
INPUT CHECK PASS: CARD 52 scenario views / 13 bases
SPLIT CHECK PASS: four disjoint held-out categories
CONTROLS: Ridge12, Isotonic1D
DEPTH FEATURE: included in Ridge12 (simulated protocol only)
DRY RUN PASS — no files written
```

- 前一项 RCTD 简单基线正式运行已从用户日志证实 `FINISHED 156 result rows`。
- 本轮 CARD **NOT_RUN**，待正式执行。下一项本地命令（仅一条）：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\simple_calibration_category_holdout.py" --method CARD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1"
```

- 预期成功：`FINISHED 156 result rows`，输出到 `D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\CARD`。如输出目录非空或报错，停止并查看完整错误，不删除/覆盖原结果。
- CARD 成功后再统一读取两法三个输出标签的指标并与同类别留出协议下的 CARR HGBC_a30、AbundanceOnly 做配对比较。52模拟视图不等于52生物重复。
