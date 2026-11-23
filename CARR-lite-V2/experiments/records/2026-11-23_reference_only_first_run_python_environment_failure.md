# 2026-11-23 CARR reference-only seqFISH+五折新实验：首次FOV0启动失败、Python双环境修复待Windows预检

## 用户Windows终端直接证据

[USER_WINDOWS_STDOUT] 用户本地新实验`--dry-run`此前成功：5个FOV检查通过（测试spot 15/13/15/14/13、10000genes；generator/map细胞分别316/479、320/485、329/494、322/485、326/486，26个mapping类型），未写新数据。

随后用户`python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\carr_reference_only_seqfishplus_batch.py" --run`，终端输出：

```text
START FOV 0
RuntimeError: train Tangram failed; log D:\Research\STdeconv_benchmark\results\CARR_reference_only_seqfishplus_20261123_v1\held_out_FOV0\logs\train_tangram.log
COMMAND D:\paper\ST_Benchmark_Planning\mvp\.venv\Scripts\python.exe D:\Research\STdeconv_benchmark\methods\Tangram\run_tangram_self_benchmark.py --base_dir ...\held_out_FOV0\synthetic_train --seed 20261123 --num_epochs 500 --mode cells --density_prior rna_count_based --device auto --max_genes 3000
...
ModuleNotFoundError: No module named 'tangram'
```

- 已成功创建新实验的`run_config.json`与FOV0的合成spot输入及日志，但**Tangram核心导入处即停止，FOV0没有完成Tangram拟合，5折训练/评价均未完成**。没有本轮指标。
- 出错根因是原批处理子进程使用`sys.executable`，当前`.venv`解释器为`D:\paper\ST_Benchmark_Planning\mvp\.venv\Scripts\python.exe`，虽然PowerShell提示同时存在`(ST_Clustering)`，但`.venv`环境中无`tangram`模块。
- 用户检查专用Conda环境并返回：
```text
Python: D:\ProgramData\miniconda3\envs\Tangram\python.exe
Tangram import PASS
CUDA: False
```
- [USER_SCREENSHOT] VS Code Python解释器列表显示专用Tangram Python3.7.12环境、ST_Clustering Python3.10.22、以及终端`.venv`。截图仅用于识别不同环境，不能推断Tangram专用环境支持GPU；实测cuda=False。

## GitHub修改：代码已提交，Windows尚未同步和执行修复版

[CARR reference-only batch](../carr_reference_only_seqfishplus_batch.py)修复：
1. 参数`--tangram-python <path>`可为Tangram子进程显式选择解释器；CARR主进程仍使用当前Python3.10的scikit-learn、pandas环境。
2. `--dry-run --resume`现在允许只读校验已有`run_config.json`并在指定Tangram解释器中实际尝试`import tangram, torch, anndata`；不会写实验输出。
3. `--run --resume`保留旧`run_config.json`匹配逻辑，新建独立`tangram_python_runtime.json`记录子进程Python路径；若已有Tangram预测但此前无解释器来源记录，则防止不明解释器混用。原失败在导入`tangram`时即停止，**未产生成功的训练映射预测文件**，可安全用新解释器恢复。
4. 预计使用CPU执行Tangram（专用环境实测`CUDA: False`），每外层FOV训练端和测试端各一次映射、共最多10次；运行速度可能比GPU慢，先观察真实首折耗时，不虚构完成时长。
5. [保护] 不建议安装/卸载/切换全部当前项目环境，也不建议删除部分输出或重跑旧实验。

## 下一步唯一Windows操作

```powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only; if ($LASTEXITCODE -eq 0) { python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\carr_reference_only_seqfishplus_batch.py" --dry-run --resume --tangram-python "D:\ProgramData\miniconda3\envs\Tangram\python.exe" }
```

预期`RESUME PREFLIGHT`、`TANGRAM_IMPORT_PASS ... CUDA False`、5个fold CHECK、`DRY RUN PASS — no files written`。若成功下一轮单条`--run --resume --tangram-python`开始继续；如果失败，用户贴完整异常而不要修改已有输出。
