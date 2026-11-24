# 2026-11-24 MERFISH独立来源：确认Squidpy预处理子集仅1只动物，改为跨切片留出（待Windows预检）

## 用户本机源数据真实输出 [USER_WINDOWS_LOG]

已下载并检查成功：`SOURCE INSPECTION PASS D:\Research\STdeconv_benchmark\data\external\MERFISH_Moffitt_2018\source_inspection.json`，无需重下：
- `GROUP Animal_ID unique 1 largest [('1',73655)]`，**无法在这份H5AD上做跨动物训练/测试隔离**。不把12个切片位置或batch充当12个独立动物。
- `GROUP Bregma unique 12`：各约5,578–6,605个细胞，12个不同原位切片位置。
- `GROUP Cell_class unique 16`：包含`Ambiguous` 9,282 个来源注释不确定的细胞；其它可见包含Inhibitory 24761、Excitatory11757、Astrocyte8393、OD Mature2 5736及多个稀有类别，其中OD Immature2仅91。
- `GROUP Behavior unique 1: Naive`；`GROUP batch unique 12`；`SPATIAL 73655 /73655 finite XY`；`NO MODEL TRAINING OR DECONVOLUTION PERFORMED`。
- 用户只贴上面部分检查日志，**X数值抽样、layers/raw字段未呈现**，不能推定X是raw integer counts。官方Squidpy为**preprocessed** MERFISH来源。新流程对这个前提不作假定，也不调用要求严格原始RNA整数counts假设的RCTD/cell2location。
- 上述为外部独立来源（Moffitt MERFISH mouse hypothalamus vs以前seqFISH+ cortex-SVZ），但只有**1个动物的多个sections**，不能声称跨动物/供体的再现性。Moffitt2018及Squidpy教程详情`https://squidpy.readthedocs.io/en/stable/notebooks/tutorials/tutorial_merfish.html`。

## 本轮代码已经提交GitHub，尚未在Windows运行

- 新增[外部MERFISH五切片分箱生成器](../prepare_merfish_moffitt_external_sections.py)：直接读取已下载的H5AD；按**数值排序的12个Bregma中的第0、3、5、8、11位**预先选择5张外层测试切片（选择仅依赖解剖坐标，不根据测试分类/结果）。
- 每个fold的训练参考仅来自其余11个sections，不允许目标切片源细胞进入reference；对训练参考按每个有确信细胞类别上限120个cell固定抽样以控制Tangram开销；后续CARR既有reference-only runner再拆为generator/mapping两池，保持其真实5FOV协议和参数。
- 测试空间伪spots根据原始MERFISH各细胞`Centroid_X,Centroid_Y`在**同一Bregma section内**进行格网分箱：每折的固定bin宽只由训练切片全部细胞坐标与密度估计（目标约10细胞/bin）；目标section仅按**全部原位细胞（含Ambiguous）占据的空间位置/数目**筛选5–24细胞bin、最多350bin，禁止根据目标细胞的真实类型/label选择bin，避免标签选择泄漏。
- `Ambiguous`标签在所有模型和目标表达/组成中一致排除，其9,282个细胞不作为已知生物类别；已占据bin的Ambiguous数量逐折报告。目标annotation-derived fractions明确**条件于已标注可识别细胞群**，不是完整native物理spot组成。表达强度来自Squidpy预处理`adata.X`的单细胞信号加和，**绝非新生成raw molecule counts**。
- 输出格式恰好兼容已经用户Windows验证的`CARR-lite-V2/experiments/carr_reference_only_seqfishplus_batch.py` 5折外层输入，参考按section隔离且在每折再做generator/mapping拆分，合成训练标签只来自训练侧。输出到`D:\Research\STdeconv_benchmark\data\external\MERFISH_Moffitt_2018\carr_sections_v1`。这里5-fold只是5个同动物的sections，非5个生物学独立样本。
- 给原CARR参考-only batch **可选参数** `--density-prior uniform`（默认仍是已完成seqFISH+的`rna_count_based`，旧协议不变）。预处理的MERFISH X总信号不可当原始RNA counts估算Tangram density prior，因此本项外部验证选`uniform`并在指标记录中单独注明不同前提。也仍需评估MERFISH source preprocessing对于跨方法定量公平的限制。
- 所有新脚本代码已提交，但本次Moffitt外部5切片测试**还没有任何新模型运行、预测或指标**；先用`--dry-run`检查负值/非有限值、实际几何bin数与类别覆盖。如果发现基础数据不满足，拒绝构造或训练，保留前序所有实验结果。

## 下一唯一Windows PowerShell命令（只读）

```powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only; if ($LASTEXITCODE -eq 0) { & "D:\ProgramData\miniconda3\envs\cell2loc_env\python.exe" "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\prepare_merfish_moffitt_external_sections.py" --dry-run }
```

预期依次打印`SOURCE 73655 cells 161 genes animals 1 sections 12`、`X SAMPLE`、5行`FOLD READY`、`DRY RUN PASS — no files written; no model training`。如遇`Preprocessed X has negative/nonfinite values`或fold类别数量不足，不得强行将表达取整或修改实验参数窥探测试表现；把原始错误发来再确定是否切换更合适的原始count数据源。通过后下一步单独执行`--prepare`生成外部只读测试输入，随后才启动CARR原runner。
