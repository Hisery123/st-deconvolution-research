# CARR-lite V2：CARD 严格类别留出输入检查通过（2026-11-22）

- **证据级别：USER_WINDOWS_STDOUT**
- 研究者 Windows PowerShell 执行：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\category_holdout_carr_v2.py" --method CARD --dry-run
```

- 用户返回的确切终端日志：

```text
FOLD stable train_views 36 test_views 16 test_bases 4
FOLD medium train_views 40 test_views 12 test_bases 3
FOLD confusable train_views 40 test_views 12 test_bases 3
FOLD lowref train_views 40 test_views 12 test_bases 3
INPUT CHECK PASS: CARD 52 scenario views / 13 bases
SPLIT CHECK PASS: four disjoint held-out categories
ABLATION: none
DRY RUN PASS — no files written
```

- **已验证的仅为输入/划分检查**；dry-run 不训练、不生成结果，不能称 CARD 类别留出已完成。
- 用户随后执行 `& d:\paper\ST_Benchmark_Planning\mvp\.venv\Scripts\Activate.ps1`，未提供该命令后的输出或提示符状态，不能确认激活结果。后续如果 Python 环境变化引发依赖错误，先检查错误，不改动实验数据。
- 上一步 RCTD 类别留出正式运行已由用户日志确认 `FINISHED 260 result rows`，独立目录 `D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\RCTD`。
- **下个唯一本地操作：正式运行 CARD 类别留出**，与 RCTD 共用本批次根目录，但不同方法子目录，遇目标文件非空时禁止覆盖：

```powershell
python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\category_holdout_carr_v2.py" --method CARD --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1"
```

- 预期成功标志 `FINISHED 260 result rows`，输出 `...\CARRliteV2_category_holdout_20261122_v1\CARD`。指标必须在运行后读取，不猜测泛化结果；52视图来自13模拟基础场景×4深度，不是独立生物重复。
