# CARR-lite V2：RCTD 严格类别留出输入检查通过（2026-11-22）

**证据等级：USER_WINDOWS_STDOUT**。用户在其 Windows PowerShell 环境执行以下命令并粘贴终端输出，助手尚未在该环境实际执行：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\category_holdout_carr_v2.py" --method RCTD --dry-run
```

原始终端：

```text
FOLD stable train_views 36 test_views 16 test_bases 4
FOLD medium train_views 40 test_views 12 test_bases 3
FOLD confusable train_views 40 test_views 12 test_bases 3
FOLD lowref train_views 40 test_views 12 test_bases 3
INPUT CHECK PASS: RCTD 52 scenario views / 13 bases
SPLIT CHECK PASS: four disjoint held-out categories
ABLATION: none
DRY RUN PASS — no files written
```

说明：52 场景输入检查和四类别拆分检查通过；默认保留已知模拟深度特征；**dry-run 没有训练、预测或写入结果**。前一行 `E5B_BS_EXIT_CODE=0` 未确定来自该 Python 进程，不作为本次成功依据。

下一步唯一待研究者本地执行的命令：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\category_holdout_carr_v2.py" --method RCTD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1"
```

预期新输出 `...\CARRliteV2_category_holdout_20261122_v1\RCTD\`；`FINISHED 260 result rows`。程序非空目标目录拒绝覆盖；若报错，不加 force、不删除已有文件，先检查。原有 13-base 对照/消融结果不受影响。

注意：category holdout 更严格，但不等于独立真实数据泛化；不把 52 views 当独立生物学重复。尚无正式训练结果。
