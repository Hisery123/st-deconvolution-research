# 2026-11-22 seqFISH+ 构建源码第81–265行审计：网格聚合、外层FOV参考排除

## 证据等级和来源

[USER_PASTED_SOURCE] 用户在本地 Windows 运行 `Get-Content` 打印 `D:\Research\STdeconv_benchmark\build_seqfishplus_real_spatial_noleak.py` 第81–265行，保留行号。此处**仅审查用户实际贴出的源码段**，没有访问用户本地文件全文、没有运行构建器，不等于已验证产生现有CSV的代码提交版本，也不等于整条训练/评价流水线无泄漏。

## 当前源码段的直接发现

1. 第81–103行：读取`annotations`（centroids/counts加载开头尚未见）、检查 `Field of View`、`Cell ID`、`X`、`Y`、`Region`、`index`、`louvain` 列存在，三张表行数必须完全一致，annotation.index与0..N-1行顺序严格一致；避免静默截断。**但三张表行数/索引一致不独立证明跨来源的细胞身份一一匹配**。
2. 第105–127行：counts转数值、要求无NA/负值，cell_type由louvain映射，cell UID由FOV/Cell ID/annotation index组合且要求唯一，再将counts/meta索引赋为cell_uid。
3. 第130–190行 `build_spots`：基于`X,Y`以`floor(coord/bin_size)`计算网格，spot ID包含FOV和bin坐标，过滤小于`min_cells`的网格；**第155行直接按spot_id将成员细胞 `target_counts` 求和**形成 `expression`；第156–159行单独用成员cell_type计数比率形成26类 `gt`；第161–189行导出位置、成员数、membership。
4. 第193–225行 `main`：args最小值校验，`counts,meta=load_and_validate`，细胞类型列表从`meta`全体标签汇总并排序；从 `Region=="Cortex"` 且 FOV∈`TARGET_FOVS`选target_meta/target_counts，再调用 `build_spots`；导出表达、真值计数/比例、location、membership和全量metadata。**因此913 metadata与514 membership差额399不应全称为“被spot阈值筛掉”——其中可能包含非Cortex/其它FOV的预先排除**。
5. 第227–264行外层留出循环：`for fov in TARGET_FOVS`，从locations中取对应FOV spot，从membership中取target cells，构建 `reference_meta=meta[Field of View != fov]`，`reference_counts=counts.loc[reference_meta.index]`，并断言`fold_target_cells`和`reference_meta.index`无交集；还要求target_types在reference_types中均有支持；第255–264行开始写出按FOV过滤的expression与gt。**证实代码包含整FOV参考排除及cell ID重叠断言。**

## 关键风险/尚未验证点

- `load_and_validate`的源码开头第1–80行尚未看到：`counts`来自何种原始定量矩阵、是否归一化、哪些基因被选入，以及标签如何映射未核实。代码`sum()`证实按成员表达数值求和，**不能在确认输入之前直接称对原始计数raw counts求和**。
- 构建器在外层划分前用全部符合条件的FOV生成target伪spot表达及各spot真值：**这本身不是泄漏**，只要预先固定网格/表达操作、训练/调参/基因筛选未看留出FOV真值或标签。训练runner会读取每个FOV的 `pseudo_spot_ground_truth.csv`，必须核查只用于评价而非拟合/特征选取。
- `all_cell_types=sorted(meta["cell_type"].unique())` 在FOV拆分前全局形成类别词表；若仅作为预设类别命名，影响有限；若类别发现/超参数由留出FOV标签驱动，则有标签信息泄漏风险，不能先宣告安全。
- `reference_meta` 包括整个`meta`中非held-out FOV细胞，未在已读片段限制`Region==Cortex`。需审查目标/参考域异质性及是否有FOV以外的批次重复；该参考与测试来自同一数据来源，不是外部独立scRNA参考。
- 未看第266行后fold的参考导出/其它边界、runner加载和训练路径、nested reference构造、任何基于所有FOV作特征统计的步骤。前序`n_overlap_cells=0`审计和`nested`字段为0只能证明对应ID检查结果，不覆盖整个训练流程。
- 70 pseudo-spots确有514个空间细胞归属及26类真值（此前70/70重建PASS）；这属于 **spatially informed pseudo-spot benchmark**，不得称直接测量的真实空间捕获spot；5 FOV不必然是5生物学独立重复。
- **无代码修改、无新训练、无宣称完全无泄漏。**

## 下一步单条只读 PowerShell

打印构建脚本的前80行与第266至340行（如果存在），带行号，补全 `load_and_validate`、参数和fold导出：

```powershell
$p="D:\Research\STdeconv_benchmark\build_seqfishplus_real_spatial_noleak.py"; $a=Get-Content -LiteralPath $p; for($i=0;$i -lt $a.Count;$i++){if($i -lt 80 -or ($i -ge 265 -and $i -lt 340)){ "{0,4}: {1}" -f ($i+1),$a[$i] }}
```

- 预期包含1–80行及266–340行范围的源码。若总行数不足340，仅打印现有行。
- 若报错或内容截断，研究者返回实际日志，不执行构建脚本、不修改文件。
