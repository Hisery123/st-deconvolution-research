# 2026-11-23 CTW原六方法无交叉参考：五环境PASS，仅CARD阻断正式运行

[USER_WINDOWS_STDOUT] 用户已同步至commit `5bd163d` 并成功使用修复后的绝对解释器方式预检：`SOURCE READY balanced_celltype 1200 train, 800 test, 419 ref, 19 types`。本次终端结尾显示`ENV SPOTlight SPOTlight PASS`与`RuntimeError: Environment preflight failed for CARD. No experiment has been launched.`。因聚合失败列表只包含CARD，可确定其他Tangram/RCTD/CellDART/cell2location/SPOTlight环境probe在这次都通过；此前用`conda run`发现的Python环境冲突已解除。**正式6法批0/24，不得记录成完成。**

原`CARD/run_CARD_generic_benchmark.R`（用户提供的10文件ZIP）前3条明确`library(CARD)`,`library(Matrix)`,`library(MuSiC)`，不可只把CARD环境名称指向RCTD以蒙混过包检查。用户`conda env list`没有CARD环境；某一R包探测输出`CARD=FALSE MuSiC=FALSE`，未显示确切被测环境；下一步仅需一次批量只读测试现有RCTD/SPOTlight/SPOTlight45/base四个R环境各自真实CARD、MuSiC、Matrix包状态。不需要再重复六方法完整预检，也不安装依赖。

[EXTERNAL VERIFIED] CARD官方安装说明`https://yma-lab.github.io/CARD/documentation/02_installation.html`和`https://github.com/YMa-lab/CARD`显示原CARD是GitHub R包，依赖MuSiC等许多R库；与现行Bioconductor CARDspa不是简单相同包名，不用它假冒原CARD基线。

[NEXT WINDOWS COMMAND] PowerShell只读枚举：
```powershell
$c="D:\ProgramData\miniconda3\Scripts\conda.exe"; foreach($e in @("RCTD","SPOTlight","SPOTlight45","base")) { Write-Output "=== $e ==="; & $c run -n $e Rscript -e "cat('CARD=',requireNamespace('CARD',quietly=TRUE),' MuSiC=',requireNamespace('MuSiC',quietly=TRUE),' Matrix=',requireNamespace('Matrix',quietly=TRUE),'\\n')" }
```
如任一环境同时CARD/MuSiC TRUE，可在批处理使用`--env-card <环境名>`重跑`--dry-run`；若全部FALSE则规划独立CARD R环境安装而不是污染其他5个已通过的方法环境。研究审计仍后置。
