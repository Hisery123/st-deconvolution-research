# 2026-11-23 CTW原六基础方法：Windows预检环境错配与直接解释器修复（正式训练仍为0/24）

## 本轮真实用户终端事实

- 用户在PowerShell下`ctw_six_baselines_cell_disjoint_batch.py --dry-run`已显示均衡/自然频率两情景输入完整（各1200 train、800 test，419 reference、19 cell types），六原始runner SHA256校验全PASS。
- 第一轮默认`conda`未在子进程PATH发现（WinError 2），用户后来使用`D:\ProgramData\miniconda3\Scripts\conda.exe`进行环境探测。
- 已有Conda探测报告：`RCTD RCTD PASS`、`SPOTlight SPOTlight PASS`，`Tangram Tangram FAIL`（`conda run ... python`导入tangram失败）、`CellDART CellDART FAIL`（导入`C:\Users\Hisery\CellDART\da_cellfraction.py`报keras缺失）、`CARD CARD FAIL`（同名Conda环境不存在）、`cell2location Cell2location FAIL`（同名Conda环境不存在）。
- 用户实际`conda env list`确认现存`Tangram`、`CellDART-GPU`、`cell2loc_env`、`RCTD`、`SPOTlight`，**不包含单独`CARD`环境**；用户贴出的R包检查输出`CARD=FALSE MuSiC=FALSE`，但粘贴中缺少对应环境标题，**不擅自认定两个R环境均缺包**。此前其它DLPFC实验已通过`D:\ProgramData\miniconda3\envs\Tangram\python.exe`直接导入tangram，故优先修正解释器调用而非重装。
- [CODE_UPDATED_NOT_WINDOWS_RUN] 研究仓库`CTW-RF/experiments/ctw_six_baselines_cell_disjoint_batch.py`已调整：原6法参数、来源分组、训练/测试边界**不变**；`--conda`默认绝对`D:\ProgramData\miniconda3\Scripts\conda.exe`；默认`CellDART-GPU`与`cell2loc_env`环境名；Tangram/CellDART/cell2location三种Python方法直接通过所选环境的`python.exe`做probe并启动训练，而不是`conda run -n`可能错选外层Python；新增可覆写`--python-tangram`/`--python-celldart`/`--python-cell2location`。R方法仍`conda run ... Rscript`并检查实际R包。
- CARD的具体R包/安装位置仍未得到PASS；CellDART-GPU是否导入成功、cell2loc_env能否导入、Tangram直接解释器是否在新batch PASS，都需要用户**下一次仅dry-run**的实际日志确认，不可自行宣称已好。无任何新六方法训练已执行（0/24）。

## 下一Windows单命令

```powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only; if ($LASTEXITCODE -eq 0) { python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_six_baselines_cell_disjoint_batch.py" --dry-run }
```

预期不写任何实验输出，打印三个`PYTHON DIRECT INTERPRETERS`路径和6条`ENV ... PASS/FAIL`；如果仅CARD缺包则再安排其独立依赖补全，不直接启动24任务，保留已有已完成实验。
