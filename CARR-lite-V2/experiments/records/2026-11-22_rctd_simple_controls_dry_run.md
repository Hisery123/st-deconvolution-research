# CARR-lite V2：RCTD 简单校准对照 Dry-run 通过（2026-11-22）

**USER_WINDOWS_STDOUT / INPUT_CHECK_PASSED_ONLY。** 用户在 Windows PowerShell 中运行：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\simple_calibration_category_holdout.py" --method RCTD --dry-run
```

控制台输出：

```text
FOLD stable train_views 36 test_views 16 test_bases 4
FOLD medium train_views 40 test_views 12 test_bases 3
FOLD confusable train_views 40 test_views 12 test_bases 3
FOLD lowref train_views 40 test_views 12 test_bases 3
INPUT CHECK PASS: RCTD 52 scenario views / 13 bases
SPLIT CHECK PASS: four disjoint held-out categories
CONTROLS: Ridge12, Isotonic1D
DEPTH FEATURE: included in Ridge12 (simulated protocol only)
DRY RUN PASS — no files written
```

- 仅验证输入 CSV 的键及预测值与真值对齐、整类别拆分和配置项。**Dry-run 无模型拟合、无指标，也没有写文件。**
- Ridge12 使用全部12个特征（包括受控模拟的已知深度比例）；Isotonic1D 只用原始目标比例。此输入方案能否在真实部署使用还需独立审查。
- **下一步一条本地命令（正式运行，未执行）：**

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\simple_calibration_category_holdout.py" --method RCTD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1"
```

- 预期末尾 `FINISHED 156 result rows`，`OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\RCTD`（每视图 Original_RCTD、Ridge12、Isotonic1D 三种输出×52视图）。
- 遇到目录非空或Python运行错误，先核对现有数据和完整日志，不删除、不强制覆盖。
