# 2026-11-23 CTW-RF 参考/训练/测试细胞ID三组拆分：Windows Dry-run PASS，正式实验待启动

## 实际终端证据 [USER_WINDOWS_STDOUT]

用户执行GitHub pull，代码更新至研究仓库commit `66f682a`，随后成功运行`ctw_cell_disjoint_reference_batch.py --dry-run`：

```text
SOURCE 836 cells 10000 genes 19 types
CELL SPLIT reference 419
CELL SPLIT train_donor 204
CELL SPLIT test_donor 213
TYPES WITHOUT TEST DONORS ['L12', 'L16', 'L17', 'L4', 'L8']
TYPES WITHOUT TRAIN DONORS ['L12', 'L16', 'L17', 'L4', 'L8']
TANGRAM_IMPORT_PASS D:\ProgramData\miniconda3\envs\Tangram\python.exe CUDA False
SMOKE PASS balanced_celltype spots 6 nnls_methods 2
SMOKE PASS cell_uniform spots 6 nnls_methods 2
PLAN scenarios ['balanced_celltype', 'cell_uniform'] x 2 Tangram runs = 4 mappings; train/test 1200 800 methods ['Tangram', 'NNLS_500', 'NNLS_marker20']
DRY RUN PASS — no files written
```

## 可确定的状态

- **只通过预检，尚未正式运行新实验**，不能填写新结果或冒充旧六方法已严格重跑。
- 五个单细胞类型只存在于reference，training/test donor中均无成员；19类型预测与分母的评价可能包含这5个零真值类型。这是数据层限制，不隐瞒，不以后验测试表现筛掉。
- Tangram当前`CUDA False`，实际运行将使用CPU；计算时长未知。
- 目标：2情景×(3 freshly generated baseline + 5 comparator) = 16 held-out metric rows；结果目录`D:\Research\STdeconv_benchmark\results\CTWRF_cell_disjoint_20261123_v1`。

## 下一用户Windows命令

```powershell
python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_cell_disjoint_reference_batch.py" --run
```

成功应依次打印`COMPLETED balanced_celltype`, `COMPLETED cell_uniform`, `BATCH FINISHED: 2 scenarios x 8 methods = 16 held-out method/scenario rows`。失败原样贴日志，保留部分输出，使用`--resume`而非删除重跑。最终Claude再集中审计。
