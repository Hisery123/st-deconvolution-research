# 2026-11-23 CTW六基础法：原CARD可复用独立R 4.5.1，统一runner调整完成；Windows dry-run待执行

## 用户实际命令及真实输出

用户Windows：

```powershell
$r="D:\R\R-4.5.1\bin\Rscript.exe"
& $r -e "cat('R_VERSION=',as.character(getRversion()),'\nCARD=',requireNamespace('CARD',quietly=TRUE),'\nMuSiC=',requireNamespace('MuSiC',quietly=TRUE),'\nMatrix=',requireNamespace('Matrix',quietly=TRUE),'\n')"
```

实际输出：

```text
R_VERSION= 4.5.1
CARD= TRUE
MuSiC= TRUE
Matrix= TRUE
警告信息:
replacing previous import 'RcppML::nmf' by 'NMF::nmf' when loading 'CARD'
```

注：namespace import masking warning不是安装失败，实际检查三包均TRUE。其余五方法Tangram/RCTD/CellDART/cell2location/SPOTlight此前统一dry-run PASS；CARD缺`CARD`名Conda env致6方法正式24任务尚未启动。

## 本次代码更改（CODE_COMMITTED_NOT_RUN）

GitHub [CTW六方法单细胞无交叉批处理](../ctw_six_baselines_cell_disjoint_batch.py) 新增`--rscript-card`默认`D:\R\R-4.5.1\bin\Rscript.exe`。仅CARD：
- preflight调用`<Rscript.exe> -e "stopifnot(requireNamespace('CARD',...), requireNamespace('MuSiC',...), requireNamespace('Matrix',...))"`；
- 正式runner调用`<Rscript.exe> D:\Research\STdeconv_benchmark\methods\CARD\run_CARD_generic_benchmark.R --base_dir <stage> --out_dir <stage/predictions> --minCountGene 5 --minCountSpot 5`；
- 写`rscript_card`绝对路径进入本次新run_config以保证以后恢复参数一致性。其余五法解释器、源细胞拆分、随机seed、输出目录、模型/融合预算均保持不变。
- **未在Windows执行新补丁**；三个R包加载TRUE不等于原CARD runner全流程成功。任何方法失败仍记日志、断点恢复，不能假定24任务已成。

## 下一用户唯一操作

```powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only; if ($LASTEXITCODE -eq 0) { python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_six_baselines_cell_disjoint_batch.py" --dry-run }
```

预期出现六项`ENV ... PASS`及`DRY RUN PASS — no experiment outputs written`，其中CARD明确显示独立`D:\R\R-4.5.1\bin\Rscript.exe`。任何报错请发日志，不启动训练。正式24任务新批仍NOT_RUN。
