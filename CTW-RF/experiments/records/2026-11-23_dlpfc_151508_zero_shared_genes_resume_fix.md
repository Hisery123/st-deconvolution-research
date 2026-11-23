# 2026-11-23 CTW DLPFC多切片：151507完成，151508零共有基因spot阻断；排除策略补丁待Windows执行

## 用户实际Windows新日志（不推断尚未执行结果）

[USER_WINDOWS_RUN_STDOUT] 在现有结果目录续跑先前NNLS_marker20回退补丁：

```text
PREFLIGHT reference_cells 6997 cell_types 7 shared_genes_all_slides 539 slides_found 12 expected 12
CELL SPLIT {'reference': 3499, 'train_donor': 2098, 'check_donor': 1400}
CALIBRATION synthetics checked; SoftOpt fallback 0 metrics not a real Visium ground-truth test
START SLIDE 151507
NNLS PANEL FALLBACK {'NNLS_marker20': 69} of 4226 spots (full-gene estimate substituted)
COMPLETED SLIDE 151507 spots 4226 labeled 4221 marker_fallback 69 top300_fallback 0 seconds 0.586
START SLIDE 151508
ValueError: Zero shared-gene total for 1 spots in D:\paper\ST_Benchmark_Planning\mvp\data\151508\filtered_feature_bc_matrix.h5
```

- **只有151507已完成**，其余151508–151676尚未有完成日志；151508目前仅确认539共有基因表达总和为0的spot数为1，未提供具体barcode。
- 151507 marker20有69/4226个spot使用全基因NNLS回退，该事件是真实运行日志。不能描述成69个全都通过marker预测。
- 此批模型使用固定原先ref/calibration细胞分组和panel；不能从Visium无真值推断精度或显著性。

## 提交补丁（CODE_COMMITTED_NOT_RUN）

对[ctw_dlpfc_multislice_application_batch.py](../ctw_dlpfc_multislice_application_batch.py)新增：
1. `exclude_zero_shared_gene_spots()`：对仅基于共有539基因的spot×gene矩阵检测行总和>0；为零的spot**不赋予均匀/伪造的细胞比例**，而是从该片有效预测输入排除；如果一张切片所有spot均零，则抛错。原H5文件不修改。
2. 每切片产生`zero_shared_gene_excluded_spots.csv`，记录spot_id、shared_gene_total、reason；`slide_summary.json`记录H5 spot总数、实际预测数、排除数；终端打印`ZERO SHARED-GENE SPOTS EXCLUDED <slide> <N> of <total>`。
3. 所有predictions与layer汇总只覆盖有效spot，已排除spot不计入预测均值与分层spot数量；每片layer匹配在有效spot集合上做。静态dry-run新增人工构造3spot（一个零行）的`ZERO-SPOT SMOKE PASS`，不写磁盘。
4. `--resume`将已完成151507视为完成并重用；新汇总字段用0排除spot作为兼容默认值，既有151507预测文件不修改；151508不存在完成标记，从头处理其未完成推断，不用删除前次输出目录。
5. 新补丁未修改原run_config计算的键和值，沿用原校准权重策略。**尚未在用户Windows测试/运行本补丁，不能提前承诺12张完成或零spot的最终分布。**

## 下一操作

用户仅需一条PowerShell带条件链的命令：

```powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only; if ($LASTEXITCODE -eq 0) { python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_dlpfc_multislice_application_batch.py" --dry-run --resume; if ($LASTEXITCODE -eq 0) { python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_dlpfc_multislice_application_batch.py" --run --resume } }
```

期望`ZERO-SPOT SMOKE PASS`/DRY RUN PASS，然后`REUSE COMPLETED SLIDE 151507`、`ZERO SHARED-GENE SPOTS EXCLUDED 151508 1 of 4384`以及余下切片COMPLETED。如果报错，保留中间数据并转录异常，不反复全面审计。
