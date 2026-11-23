# 2026-11-23 CTW-RF严格参考/伪spot来源细胞隔离：原六方法批处理编写完毕，待Windows环境预检

## 上传源码证据和真实状态

[USER_UPLOADED_ZIP_READ] 用户Windows实际压缩并上传`CTW_six_method_runners.zip`，助手已读取ZIP的**10个真实源码文件**，而非仅凭名称推测接口。ZIP大小30,387 bytes，SHA256=`dfd1f15363aaeb55e15f22da9790d432b56c0bbf4824a8929048468066538d0e`。研究主运行器只使用其中的六个实际算法入口（其它四个自基准和52场景批运行器用于了解已有命令格式）：

| 算法 | 本机路径（`D:\Research\STdeconv_benchmark\methods\`相对路径） | 主输出 |
|---|---|---|
| Tangram | `Tangram\run_tangram_self_benchmark.py` | `Tangram_self_benchmark.csv` |
| RCTD | `RCTD\run_RCTD_generic_benchmark.R` | `RCTD_self_benchmark.csv` |
| CellDART | `CellDART_original\run_CellDART_generic_benchmark.py` | `CellDART_self_benchmark.csv` |
| CARD | `CARD\run_CARD_generic_benchmark.R` | `CARD_self_benchmark.csv` |
| cell2location | `Cell2location\run_cell2location_self_benchmark.py` | `Cell2location_self_benchmark.csv` |
| SPOTlight | `SPOTlight\SPOTlight.R` | `SPOTlight_self_benchmark.csv` |

这些实际源码都读取`--base_dir`目录下的`pseudo_spot_expression.csv`、`sc_reference_counts.csv`、`sc_reference_labels.csv`、`pseudo_spot_locations.csv`，将spot×celltype结果写到`predictions/`。R方法用`Rscript`和其必要包，Python方法需要各自Python环境。用户尚未在新严格六方法runner上执行dry-run/run，**24基础任务和完整六法结果完全未开始**。

## 批处理承诺与边界

[CODE_COMMITTED_NOT_RUN] 新建[ctw_six_baselines_cell_disjoint_batch.py](../ctw_six_baselines_cell_disjoint_batch.py)，已内置10文件ZIP里所选六原始算法入口的SHA256逐项检查、环境依赖只读probe（`conda run -n ENV python/Rscript`），未经核实环境不会正式启动新算法训练。

1. 数据来源固定为已完成`D:\Research\STdeconv_benchmark\results\CTWRF_cell_disjoint_20261123_v1`的两个场景`balanced_celltype`与`cell_uniform`，各`train`1200spot与`test`800spot，419 reference cells、204 train donor cells、213 test donor cells、19类。再利用已保存`source_cell_partition.csv`和各spot`train_membership.csv`/`test_membership.csv`确认输入cell ID隔离，**不复制旧预测、不根据新测试结果重构伪spot**。
2. 在新结果文件夹`D:\Research\STdeconv_benchmark\results\CTWRF_six_method_disjoint_20261123_v1\views\<scenario>\<train|test>`**复制**每子任务四个源CSV，提供统一输入。真实训练/测试比例真值始终保留在原项目`ground_truth_and_membership`下，**绝不写入任何算法读入的`--base_dir`**，模型本身仅见输入表达/参考和分组，融合训练见train真值，测试真值仅最后评分。
3. 两情景×2(train/test)×6方法=24次独立基础方法运行。预置命令来自用户上传实际脚本：Tangram默认500epoch/3000gene/auto; RCTD full/doublet/4cores/CELL_MIN_INSTANCE2; CellDART 20000 synthetic/3000 iterations; CARD minCountGene5,minCountSpot5; cell2location原版参考250epoch、map20000epoch、CPU、8cells/loc、posterior1000；SPOTlight cl_n3/hvg2000。**这些配置是各算法既有参数，不构成等耗时或等模型容量公平对照**。
4. 软件环境默认根据已有文件夹/历史52scenario名字尝试Conda `Tangram, RCTD, CellDART, CARD, Cell2location, SPOTlight`。这是**候选环境名、尚未验证全部存在**；dry-run逐个测试Tangram/tangram、spacexr、CellDART、CARD/MuSiC、cell2location/scvi、SPOTlight/Seurat，任何缺失直接标识并拒绝开始训练。支持`--env-tangram`/`--env-rctd`/`--env-celldart`/`--env-card`/`--env-cell2location`/`--env-spotlight`按真实环境改名，无依赖自动安装。
5. 逐方法检查预测必须包含全部spot IDs、19 celltypes、非负有限值、行和正常（与1偏差不超过0.01），不可静默替换缺失类别或把零预测填随机值；RCTD、SPOTlight会过滤参考细胞数很少的类别（原算法固有行为）并补0类别，异常报错必须保留。
6. 24项有效后，在same train/test和same six predictions基础上拟合/evaluate `strong2`、`expanded4`、`full6`历史对照池，输出各单方法、EqualWeight、GlobalStacking、CTW_HardSelect、CTW_InvRMSE_p2、CTW_SoftOpt共每场景27行（2+5、4+5、6+5=27；两场景合计54行），所有权重只用train真值，test donor truth用于最终JSD/RMSE。
7. 每任务单独`logs`，`baseline_task_status.csv`会在每项结束后刷新；任何方法失败其余方法尽量继续，未全部成功时拒绝生成/宣称六法完整评测；`--run --resume`复用有效已完成预测，隔离`.rejected_*.csv`无效中间预测以便重试，不删旧文件。
8. 计算负担提示：cell2location原脚本CPU并做**4次**20000epoch mapping和250epoch reference训练，可能很耗时；严禁给用户未经执行的运行时间估计。必要时基于用户硬件和完成结果透明记录减少预算后的方案，但那是新配置，不得混成默认原版历史设置。

## 下一步严格单命令

请Windows运行：

```powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only; if ($LASTEXITCODE -eq 0) { python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_six_baselines_cell_disjoint_batch.py" --dry-run }
```

期望每场景`SOURCE READY ...`、六项`RUNNER SHA256 PASS ...`、六项`ENV ... PASS`、最终`DRY RUN PASS — no experiment outputs written`。任何ENV失败请发该行输出，不要安装包或正式运行。所有新实验指标保持`NOT_RUN`直到实际用户Windows输出。研究者要求最终再集中审核；此处环境probe是自动运行前检查，而不是额外碎片研究审计。
