# 2026-11-22 seqFISH+ 空间细胞聚合伪spot：来源首轮核查

## 用户Windows终端直接证据（2026-11-22）

读取根目录：`D:\Research\STdeconv_benchmark\data\groundtruth\seqfishplus_cortex_real_spatial_noleak`，四份文件的`SHAPE`、列名和前两行。**这是原始CSV读取日志；源CSV字节和构建脚本尚未取得，原始真值一致性尚未独立校验。**

1. `cell_metadata_aligned.csv`：**(913, 9)**；列包括 `cell_uid`, `Field of View`, `Cell ID`, `X`, `Y`, `Region`, `annotation_index`, `cell_type`, `cell_uid.1`。样例 `FOV0_C1_I0` 归属于FOV0、Cell ID1、X1305.70/Y414.98、Cortex、L13；`FOV0_C2_I1` 为L3。
2. `spot_cell_membership.csv`：**(514, 9)**；列包括 `cell_uid`, `spot_id`, `fov`, `Cell ID`, `X`, `Y`, `Region`, `annotation_index`, `cell_type`。样例 `FOV0_C1_I0` 归入 `FOV0_X2_Y0`，`FOV0_C2_I1` 归入 `FOV0_X1_Y0`。
3. `pseudo_spot_locations.csv`：**(70, 10)**；`spot_id`,`fov`,`bin_x`,`bin_y`,`centroid_x`,`centroid_y`,`n_cells`,`n_cell_types`,`grid_center_x`,`grid_center_y`。样例FOV0_X0_Y0 grid center (250,250)，7 cells、5 types；FOV0_X0_Y1 grid center (250,750)，11 cells、7 types。
4. `pseudo_spot_ground_truth.csv`：**(70, 27)**；`spot_id`及 `L1`至`L26`。FOV0_X0_Y0真值按1/7的步长出现：L3/L9/L13/L25各1/7、L6为3/7；FOV0_X0_Y1按1/11步长。

## 可以支持的研究判断

- 这70个spot有明确的网格单元（`bin_x`/`bin_y`）和单细胞归属表；真值具有成员计数比例形式，因此可以判定是**基于真实seqFISH+空间定位细胞，进行空间网格聚合得到的 pseudo-spots**，不是独立仪器直接捕获的真实空间spot。
- 913条细胞metadata与514条membership并不等价于已经验证913个各异细胞/514个各异成员。只有核验`cell_uid`唯一性、member是否完全属于metadata、每spot成员数与`n_cells`一致及26类真值一致以后，才能下最终构造质量结论。514未进入membership的其它399个metadata行的筛除条件尚不明确。
- 真实FOV0-FOV4空间坐标与细胞类型来自实验数据，是semi-synthetic/spatially informed pseudo-spot基准；**不能表述成在直接测得的70个真实空间spot上做独立验证**。
- 以前折叠指标`mean_spot_JSD`及`singleton_vs_zero_AUPRC`真实存在、且FOV2为三分支检测失败；但“完全no leakage”仍待对数据源、参考排除代码、特征工程/阈值调参边界的独立核验。
- 5FOV不是5个独立供体；70spot不是70个独立生物学重复；未报告统计显著性。
- 此后论文建议分类为：**spatially informed pseudo-spot benchmark derived from seqFISH+ single-cell spatial coordinates**。中文版：基于seqFISH+真实空间定位单细胞构建的聚合伪spot基准。

## 下一步唯一人工步骤（只读不训练）

本地检查 `spot_cell_membership.csv` 是否在细胞ID、spot ID、spot内细胞数和26类真值方面与metadata、location、ground truth一致。先只做核查，不改变文件、不补空间点位图。如不匹配输出错误统计和样例，再检查来源脚本。

可用单条PowerShell命令：

```powershell
python -c "import pandas as pd,numpy as np; from pathlib import Path; r=Path(r'D:\Research\STdeconv_benchmark\data\groundtruth\seqfishplus_cortex_real_spatial_noleak'); m=pd.read_csv(r/'cell_metadata_aligned.csv'); a=pd.read_csv(r/'spot_cell_membership.csv'); l=pd.read_csv(r/'pseudo_spot_locations.csv'); t=pd.read_csv(r/'pseudo_spot_ground_truth.csv'); cs=[f'L{i}' for i in range(1,27)]; p=pd.crosstab(a.spot_id,a.cell_type).reindex(index=t.spot_id,columns=cs,fill_value=0); n=p.sum(axis=1); pred=p.div(n,axis=0); delta=np.abs(pred.to_numpy()-t[cs].to_numpy()); sizes=a.groupby('spot_id').size().reindex(l.spot_id); print('COUNTS metadata/membership/spots',len(m),len(a),len(l)); print('ID CHECK metadata_unique/member_unique/member_subset',m.cell_uid.is_unique,a.cell_uid.is_unique,set(a.cell_uid).issubset(set(m.cell_uid))); print('SPOT CHECK unique/truth_match/membership_match',l.spot_id.is_unique,set(l.spot_id)==set(t.spot_id),set(l.spot_id)==set(a.spot_id)); print('SPOT SIZE CHECK',int(sizes.notna().sum()),'of',len(l),'mismatched',int((sizes.to_numpy()!=l.n_cells.to_numpy()).sum())); print('GROUND TRUTH MAX ABS ERROR',float(np.nanmax(delta)),'MISMATCHED SPOTS',int((delta>1e-9).any(axis=1).sum()))"
```

- 预期三个ID标志为True，三个spot标志为True，spot mismatched=0，GROUND TRUTH MAX ABS ERROR≈0（浮点小偏差允许≤1e-9）。
- 若命令报错或任何条件不通过，保留原始数据，贴出输出并检查代码/规则，不强制修正数据。
