# 2026-11-23 CTW DLPFC 12张切片真实应用批处理：Windows Dry Run PASS（尚未正式运行）

## 来自研究者Windows的真实终端

执行`ctw_dlpfc_multislice_application_batch.py --dry-run`成功，日志：

```text
PREFLIGHT reference_cells 6997 cell_types 7 shared_genes_all_slides 539 slides_found 12 expected 12
CELL SPLIT {'reference': 3499, 'train_donor': 2098, 'check_donor': 1400}
SLIDE 151507 {'n_spots': 4226, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 4221, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151508 {'n_spots': 4384, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 4381, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151509 {'n_spots': 4789, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 4788, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151510 {'n_spots': 4634, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 4595, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151669 {'n_spots': 3661, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 3636, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151670 {'n_spots': 3498, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 3484, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151671 {'n_spots': 4110, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 4093, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151672 {'n_spots': 4015, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 3888, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151673 {'n_spots': 3639, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 3611, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151674 {'n_spots': 3673, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 3635, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151675 {'n_spots': 3592, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 3566, 'layer_source': 'manual_layer_annotations.csv:layer'}
SLIDE 151676 {'n_spots': 3460, 'n_h5_genes': 33538, 'n_ref_common_genes': 539, 'layer_labeled': 3431, 'layer_source': 'manual_layer_annotations.csv:layer'}
SMOKE PASS 4 synthetic spots 3 NNLS methods; feature_counts {'NNLS_all': 539, 'NNLS_top300': 300, 'NNLS_marker20': 140}
DRY RUN PASS — no files written
```

## 状态与限制

- 12/12张实际DLPFC H5已被发现，预检显示每张皮层layer标签可匹配绝大多数spots；**尚未正式运行任何12张切片推断**，没有新CTW外部应用结果。
- 模型使用既有7类、539共有基因reference_70，固定NNLS all/top300/marker20三基线+5融合/对照共8方法，属于**补充应用**而非旧六基础方法的多切片重跑。
- 单细胞参考分成3499 reference profiles、2098 train donors、1400 check donors；Synthetic spot真值只在内部校准/检查使用；Visium真实切片无组成比例真值。
- 禁止将layer标签当celltype组成真值计算JSD/RMSE，或将spot数当独立供体数；用户要先继续跑实验，审计统一后置。

## 下一步唯一PowerShell

```powershell
python "D:\Research\st-deconvolution-research\CTW-RF\experiments\ctw_dlpfc_multislice_application_batch.py" --run
```

成功标志：`COMPLETED SLIDE` ×12，`BATCH FINISHED 12 DLPFC slices; 96 slice-method prediction matrices`。失败则保留中间结果并用`--run --resume`继续，不提前宣称成功。
