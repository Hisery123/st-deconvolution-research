# 2026-11-22 seqFISH+：伪spot成员与26类真值重算一致性检查（通过）

## 原始用户 Windows 终端证据

研究者在本机读取：
- `cell_metadata_aligned.csv`（913行）
- `spot_cell_membership.csv`（514行）
- `pseudo_spot_locations.csv`（70行）
- `pseudo_spot_ground_truth.csv`（70行，L1至L26）

使用 `pandas.crosstab(a.spot_id,a.cell_type)` 并按真值文件 `spot_id` 和26类重排，除以每spot成员数构建计数比例，再与 `pseudo_spot_ground_truth.csv` 逐元素绝对差比较。用户粘贴输出：

```text
COUNTS metadata/membership/spots 913 514 70
ID CHECK metadata_unique/member_unique/member_subset True True True
SPOT CHECK unique/truth_match/membership_match True True True
SPOT SIZE CHECK 70 of 70 mismatched 0
GROUND TRUTH MAX ABS ERROR 8.326672684688674e-17 MISMATCHED SPOTS 0
```

## 已证实的范围

1. `cell_uid` 在913条metadata与514条membership内各自唯一，514条membership cell_uid全部存在metadata中。
2. 70个pseudo spot的ID在location与truth之间集合一致，也与membership引用的spot ID集合一致；location的spot_id唯一。
3. 70/70 spot的记录 `n_cells` 等于 `spot_cell_membership.csv` 中spot_id出现次数；没有不匹配。
4. 根据membership记录的26种 `cell_type` 所算的细胞计数比例与70×26真值矩阵完全一致（数值最大误差约8.33e−17，等于浮点舍入级别；大于1e−9的偏差spot为0）。
5. **验证的是cell-to-spot关系与ground truth自洽，不代表** 已检查原始seqFISH+数据来源、RNA计数矩阵聚合方式、测试FOV与参考/伪训练/选特征/调参全过程的隔离，也未审计选择514/913细胞的筛选规则。当前基准是以有真实位置的单细胞构建的**spatially informed pseudo-spots**，不是70个独立仪器测量的真实spot。

## 下一步（手动，一条命令，不训练）

先只读查看`pseudo_spot_expression.csv`的维度、字段、spot对齐及非负/缺失情况，确定后续表达聚合与来源代码审查对象：

```powershell
python -c "import pandas as pd,numpy as np; from pathlib import Path; r=Path(r'D:\Research\STdeconv_benchmark\data\groundtruth\seqfishplus_cortex_real_spatial_noleak'); e=pd.read_csv(r/'pseudo_spot_expression.csv'); t=pd.read_csv(r/'pseudo_spot_ground_truth.csv'); v=e.drop(columns=['spot_id'],errors='ignore').select_dtypes(include='number'); print('EXPRESSION SHAPE',e.shape,'SPOT_ID_PRESENT','spot_id' in e.columns,'SPOT_IDS_MATCH',('spot_id' in e.columns and e.spot_id.is_unique and set(e.spot_id)==set(t.spot_id))); print('FIRST COLUMNS',list(e.columns[:12])); print('NUMERIC FEATURES',v.shape[1],'NONFINITE VALUES',int((~np.isfinite(v.to_numpy())).sum()),'NEGATIVE VALUES',int((v.to_numpy()<0).sum()),'ALL_ZERO_ROWS',int((v.sum(axis=1)==0).sum())); print('FIRST TWO IDS',e.spot_id.head(2).to_list() if 'spot_id' in e.columns else 'NO_ID')"
```

预期`EXPRESSION SHAPE`、`SPOT_IDS_MATCH True`、数值特征计数与缺失/负值记录；如测试失败，不更改文件，回报完整输出。
