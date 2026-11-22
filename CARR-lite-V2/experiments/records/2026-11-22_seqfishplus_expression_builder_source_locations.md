# 2026-11-22 seqFISH+ pseudo_spot_expression.csv 生成源码定位（仅用户终端grep）

## 用户 Windows 原始定位信息

- 用户在本地 `D:\Research\STdeconv_benchmark` 目录递归搜索 Python 源码中包含字符串 `pseudo_spot_expression.csv` 的行（`Get-ChildItem *.py | Select-String -SimpleMatch`）。
- 最关键匹配：
  - `D:\Research\STdeconv_benchmark\build_seqfishplus_real_spatial_noleak.py:218`：`write_csv(expression, args.out_dir / "pseudo_spot_expression.csv", "spot_id")`，写出表达CSV。
  - 同脚本第257行：`fold_dir / "pseudo_spot_expression.csv"`，涉及fold输出。
  - `D:\Research\STdeconv_benchmark\run_carr_lite_v2_seqfishplus_5fold.py:112`：`fold / "pseudo_spot_expression.csv"`，五折runner读取该文件。
- 其它类似文件名的构建脚本在 `data\groundtruth\` 以及方法目录也出现匹配；由于本次目标为 `seqfishplus_cortex_real_spatial_noleak`，先查同名`build_seqfishplus_real_spatial_noleak.py`，**不能仅凭grep定位就断言实际运行的是哪一版本、是否存在泄漏**。

## 下一步唯一人工步骤：只读查看关键构建源码

从 `build_seqfishplus_real_spatial_noleak.py` 打印第81–265行，带行号，重点查看 `expression` 变量生成、基因筛选、成员细胞聚合、fold分割，不能执行脚本和覆写数据：

```powershell
$script = "D:\Research\STdeconv_benchmark\build_seqfishplus_real_spatial_noleak.py"; $lines = Get-Content -LiteralPath $script; for ($i = 80; $i -lt [Math]::Min(265, $lines.Count); $i++) { "{0,4}: {1}" -f ($i + 1), $lines[$i] }
```

若无文件、编码或内容被截断，贴完整错误；不要修改或重新跑构建脚本。

## 仍待核查的科研问题

- 70个pseudo spots源于514条真实空间定位细胞的网格聚合（前序已确认；26类组成真值重建70/70 PASS）。
- 10000基因是否来自源空间单细胞表达、单细胞参考、外部过滤还是用了留出测试真值选择？
- 514/913细胞筛选及pseudo spot表达计算：汇总原始counts还是归一化值？
- FOV隔离在哪里执行？训练参考、特征工程和参数选择是否用到测试FOV？
- 本次只是grep路径，未见源码，不提前声称无泄漏。
