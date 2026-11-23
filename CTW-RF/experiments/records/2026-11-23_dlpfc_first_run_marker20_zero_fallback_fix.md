# 2026-11-23 CTW DLPFC多切片首跑在151507 NNLS_marker20零解中断；边界修复已提交，Windows待恢复

## 用户Windows原始失败证据

[USER_WINDOWS_RUN_STDOUT] 用户正式执行`ctw_dlpfc_multislice_application_batch.py --run`（此前12/12张DLPFC的dry-run PASS，7类/539genes/reference3499/train2098/check1400）。运行显示：

```text
CALIBRATION synthetics checked; SoftOpt fallback 0 metrics not a real Visium ground-truth test
START SLIDE 151507
Traceback ...
  File "...ctw_dlpfc_multislice_application_batch.py", line 498, in main
    base = nnls_predict(observed, profiles, features, classes)
  File "...ctw_dlpfc_multislice_application_batch.py", line 258, in nnls_predict
    raise ValueError("NNLS zero solution: " + method +
ValueError: NNLS zero solution: NNLS_marker20, spot AACTTTCTCGATCATG-1
```

- synthetic donor检查/SoftOpt训练已成功，**真实Visium切片151507尚未完成，一张切片都不能算成功**。
- 正式运行创建的`D:\Research\STdeconv_benchmark\results\CTWRF_DLPFC_multislice_20261123_v1`以及run_config和部分校准输出应保留。数据未遭系统删除或重新构建。
- 零解发生在限制标记基因子集`NNLS_marker20`，不等于全部spot没有任何基因表达。是否具体是全体marker为0或其他数值支持不足，**前述错误未提供诊断，仅能确认NNLS零解**。

## 提交的处理（CODE_COMMITTED_NOT_RUN）

修复[ctw_dlpfc_multislice_application_batch.py](../ctw_dlpfc_multislice_application_batch.py)：
1. NNLS先用共有539基因得`NNLS_all`，在`NNLS_top300`或`NNLS_marker20`出现零解时，**对该spot使用已算出的`NNLS_all`预测作为预设有限面板的缺失支持回退**；如果`NNLS_all`本身为零解/非有限则仍报错，不制造随机/均匀预测。
2. 逐spot诊断输出`<slide>/nnls_panel_fallback_spots.csv`：spot_id、出错基础法、回退算法、零解原因（可区分selected marker signal为0和有信号但NNLS为0）、selected_gene_signal_fraction。每切片slide_summary.json增加`nnls_panel_fallback_count`/marker20/top300数量，终端打印累计回退数量，**避免把回退spot当原标记面板成功预测**。
3. `--dry-run --resume`在既有run_config匹配后，用人造“marker silent”输入验证回退路径，**不写盘**；`--run --resume`保持原配置字典不改，因此能恢复首跑中断的151507，而不用删结果重跑旧批次。
4. 本项属于对真实数据低marker信号的固定数值边界处理；不能把回退次数完全忽略、不能称后验调门控权重或对真实比例真值优化。原synthetic donor的校准结果/训练协议未变。

## 下一用户唯一Windows PowerShell操作

```powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only; if ($LASTEXITCODE -eq 0) { python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_dlpfc_multislice_application_batch.py" --dry-run --resume; if ($LASTEXITCODE -eq 0) { python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_dlpfc_multislice_application_batch.py" --run --resume } }
```

预期dry-run除12SLIDE、`SMOKE PASS`外，新增`NNLS PANEL FALLBACK`、`FALLBACK SMOKE PASS`并`DRY RUN PASS — no files written`；通过后单条命令自动恢复正式运行。不能预先宣称实测修复成功或12张切片完成。
