# 2026-11-22 seqFISH+ 伪spot表达矩阵只读完整性核查

## 用户本地命令及原始输出

[USER_WINDOWS_STDOUT] 研究者在 Windows `ST_Clustering` 环境读取：

- `D:\Research\STdeconv_benchmark\data\groundtruth\seqfishplus_cortex_real_spatial_noleak\pseudo_spot_expression.csv`
- 同目录 `pseudo_spot_ground_truth.csv`

核查表形状、spot ID唯一且集合与ground truth一致、数值特征数、非有限值、负值、全零spot行。用户原样终端输出：

```text
EXPRESSION SHAPE (70, 10001) SPOT_ID_PRESENT True SPOT_IDS_MATCH True
FIRST COLUMNS ['spot_id', '1700022a21rik', '1700025g04rik', '4933401b06rik', '5830417i10rik', '9330102e08rik', '9430018g01rik', '9430083a17rik', 'Aanat', 'Aasdh', 'Aatf', 'Abat']
NUMERIC FEATURES 10000 NONFINITE VALUES 0 NEGATIVE VALUES 0 ALL_ZERO_ROWS 0
FIRST TWO IDS ['FOV0_X0_Y0', 'FOV0_X0_Y1']
```

## 已得到的结论与不能推出的结论

- 70个pseudo-spot记录、1列spot ID和10000列数值表达；spot ID唯一且与70个真值spot ID集合完全对应。
- 10,000列数值无 NaN、Inf、负值；70行均非全零。
- 结合已验证的`spot_cell_membership.csv`、`pseudo_spot_ground_truth.csv`和`pseudo_spot_locations.csv`，本批**真实seqFISH+空间细胞的网格聚合伪spot基准**在ID、成员数量、26类真值、表达矩阵的基础内部一致性良好。
- **未核查**：表达是否来自成员细胞原始RNA矩阵，count汇总/均值/归一化/挑基因具体方式、何时生成10,000基因列表、基因列表是否受测试FOV真值选择影响、是否在模型/参考隔离之外使用测试FOV信息；因此不得称“完全无泄漏”或“独立测量的真实空间spot”。也未独立验证原始CSV字节。

## 下一步：定位表达构建脚本，不训练

在用户 Windows 项目源码搜索包含 `pseudo_spot_expression.csv` 的 Python 文件，以便审计生成语句和特征挑选，优先在基准项目目录进行：

```powershell
Get-ChildItem -Path "D:\Research\STdeconv_benchmark" -Recurse -File -Filter "*.py" -ErrorAction SilentlyContinue | Select-String -SimpleMatch "pseudo_spot_expression.csv" | Select-Object -First 25 Path,LineNumber,Line
```

- 预期输出可能包含生成此CSV的脚本路径及行号；也可能只是读取它的后续分析脚本，需要看完整代码区分。
- 如果无输出，不说明脚本不存在；再去`D:\Research\TRUST_Deconv`或GitHub源码镜像搜索，不猜想执行成功。
- 一次仅给研究者一条PowerShell命令；只读源码，无训练、无文件改动。
