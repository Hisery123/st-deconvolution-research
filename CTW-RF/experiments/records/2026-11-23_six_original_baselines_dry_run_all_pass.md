# 2026-11-23 CTW-RF 严格细胞来源隔离六原始方法：Windows dry-run全部PASS，24方法任务待正式执行

## 用户Windows实际输出 [USER_WINDOWS_STDOUT]

用户成功从GitHub拉取至`51aacf3`并执行`ctw_six_baselines_cell_disjoint_batch.py --dry-run`，确认：

```text
SOURCE READY balanced_celltype 1200 train spots, 800 test spots, 419 reference cells, 19 cell types
SOURCE READY cell_uniform 1200 train spots, 800 test spots, 419 reference cells, 19 cell types
RUNNER SHA256 PASS Tangram D:\Research\STdeconv_benchmark\methods\Tangram\run_tangram_self_benchmark.py
RUNNER SHA256 PASS RCTD D:\Research\STdeconv_benchmark\methods\RCTD\run_RCTD_generic_benchmark.R
RUNNER SHA256 PASS CellDART D:\Research\STdeconv_benchmark\methods\CellDART_original\run_CellDART_generic_benchmark.py
RUNNER SHA256 PASS CARD D:\Research\STdeconv_benchmark\methods\CARD\run_CARD_generic_benchmark.R
RUNNER SHA256 PASS cell2location D:\Research\STdeconv_benchmark\methods\Cell2location\run_cell2location_self_benchmark.py
RUNNER SHA256 PASS SPOTlight D:\Research\STdeconv_benchmark\methods\SPOTlight\SPOTlight.R
BUDGET cell2location 250 reference epochs and 20000 map epochs * 4 runs (CPU by original runner); CellDART iterations 3000 * 4 runs
PYTHON DIRECT INTERPRETERS {'Tangram': 'D:\\ProgramData\\miniconda3\\envs\\Tangram\\python.exe', 'CellDART': 'D:\\ProgramData\\miniconda3\\envs\\CellDART-GPU\\python.exe', 'cell2location': 'D:\\ProgramData\\miniconda3\\envs\\cell2loc_env\\python.exe'}
CARD DIRECT RSCRIPT D:\R\R-4.5.1\bin\Rscript.exe
CONDA conda 25.9.1
ENV Tangram D:\ProgramData\miniconda3\envs\Tangram\python.exe PASS
ENV RCTD RCTD PASS
ENV CellDART D:\ProgramData\miniconda3\envs\CellDART-GPU\python.exe PASS
ENV CARD D:\R\R-4.5.1\bin\Rscript.exe PASS
ENV cell2location D:\ProgramData\miniconda3\envs\cell2loc_env\python.exe PASS
ENV SPOTlight SPOTlight PASS
PLAN 2 sampling scenarios x 2 train/test x 6 original baseline runners = 24 tasks then 2 scenarios x 3 matched method pools
DRY RUN PASS — no experiment outputs written
```

## 当前严格状态

- [DRY_RUN_COMPLETE] 全部六原始算法runner源码hash及对应依赖环境通过此轮只读预检：**6/6**。先前仅CARD包缺失是环境路径错配，用户本机独立R4.5.1现已通过检查；无须新建CARD Conda环境。
- [OFFICIAL_RUN_NOT_STARTED] 本批六方法跨两场景24个训练/预测任务**尚未实际运行**，没有六法新评测成绩。不能把预检当实验结果或与已完成三基线补充实验混合。
- 一致性：两个场景、419 mapping reference、1200 synthetic train /800 synthetic test、19种细胞类型；来源cell ID独立。正式batch不会使用之前重叠reference的旧六法预测，最终才执行strong2/expanded4/full6三方法池各融合。统计生物独立性仍有限于原cortex-SVZ来源，最终审计再统一处理。
- 预计计算开销大：cell2location参考250 epochs + 映射20000epochs ×4，CellDART 3000 iterations ×4；未估计任务完成时间。
- 下一用户唯一Windows命令：
```powershell
python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_six_baselines_cell_disjoint_batch.py" --run
```
- 每任务后更新`D:\Research\STdeconv_benchmark\results\CTWRF_six_method_disjoint_20261123_v1\baseline_task_status.csv`，单独`logs/`。若部分失败，不删新结果目录，`--run --resume`复用有效预测；全部6×2×2成功后应打印`BATCH FINISHED 2 scenarios, 24/24 base method runs, 6 matched pool evaluations; 54 held-out metric rows`，并生成跨场景与方法池的CSV。用户坚持先完整补实验，综合论文审计留最后。
