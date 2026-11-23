# 2026-11-23 用户提供完整CARR-lite V2 seqFISH+五FOV运行器源码：后续reference-only训练实验设计

## 证据

[USER_PASTED_SOURCE] 用户用`Get-Content -Raw D:\Research\STdeconv_benchmark\run_carr_lite_v2_seqfishplus_5fold.py`输出完整脚本，本次以粘贴文本(2)直接取得源码、并在助手容器从终端开头的shebang到结束if-main提取，**已通过Python compile语法检查**；但没有从GitHub取得这份runner的历史提交SHA，也没有在用户Windows执行它。本次用户同时上传粘贴文本(1)，从`genes = expression.columns.intersection(...)`开始，是该脚本中后段的重复片段，不能当第二套独立源码。

## 已确认的代码结构

- `load_fold`读取held-out FOV的pseudo_spot_ground_truth、counts、expression、locations、sc_reference_counts、labels，以及`predictions/Tangram_self_benchmark.csv`。
- `nested_reference(train,test)`通过两者参考ID交集得到剔除两FOV细胞的参考；`reference_profiles`计算分型平均表达；`type_definitions`创建marker40/confusion3。
- `build_candidates`返回全部spot×celltype的12个模型输入特征，**同时附带truth_abundance、truth_count、delta、presence、singleton**。这些是训练标签/评价辅助字段，不应输入特征或用于测试组参数拟合；`fit_models`仅用train_candidates的12维和delta/abundance/presence拟合三分支HGBC。
- `main`对每个外层heldout FOV，用其他4个真实FOV组成训练候选、nested_reference保证参考排除outer和train FOV；注意其中的训练标签来自**其它FOV的已知组成真值**，**不是**只从参考单细胞合成伪spot的训练方案。现有工作已跑过，不应作为C3新结果重复执行。
- `make_predictions`对test候选只读12个特征做推理，但数据结构里会加载test真值用于index/columns和后续评价；后续reference-only训练工具应将真值读取限制在评价阶段，明确测试fold/参考边界。
- 输出原地固定`batch_runs/CARR_lite_V2_sensitivity_ablation`，新实验不能直接调用旧main，否则可能复写历史结果；可以将原runner作为只读导入的功能模块，输出到独立子目录。

## 新C3实验部署方案：只用参考细胞生成训练真值，应用到留出FOV

1. 每个outer FOV保持现有Tangram预测与target spot表达不变，测试真值仅最后评价。
2. 训练材料仅从外层fold提供的`sc_reference_counts/sc_reference_labels`构造模拟伪spots；先划分细胞ID为模拟生成池/基础预测或参考profile池，避免同一参考细胞既做模拟训练spot又用来“重建/预测”自身。这些参考细胞来自同一个seqFISH+原始数据域，不可冒称独立外部scRNA-seq平台数据。
3. 生成多个预声明配置（如固定随机种子与每spot cell count、训练spot数），将基因级表达按细胞求和，cell count生成组成真值。必须维持每个测试FOV中reference被排除、其类别受支持，输出真实完整测试FOV及负结果。
4. **关键待解决技术接口：训练伪spot的基础反卷积预测必须来自与目标fold Tangram一致的算法和参考协议**，否则改用NNLS/理想真值加噪会使校准器训练输入域与测试域不一致并混淆因果比较。当前已收到的CARR runner只读取现成Tangram预测文件，不包含Tangram生成/映射函数。
5. 因此下一步必须取得用户现有`D:\Research\STdeconv_benchmark\run_tangram_seqfishplus_5fold.py`的完整源码，核实其函数可否复用或需要隔离输出生成新伪spot预测。**在此之前不提交看似能运行但方法不公允的训练脚本**。
6. 新脚本设计方向：一条batch命令做5个留出FOV×多种预先声明训练spot数，目录另存；`--dry-run`仅检查必要文件、基因/细胞类/参考+Tan脚本接口，成功后`--run`；输出逐FOV指标、训练来源审计、模型日志和配置，避免改旧数据或重复历史实验。
7. 70个spot为基于空间位置汇聚的pseudo spots；5 FOV未证明5个独立生物样本。标签为技术分组，不能写为独立scRNA-seq供体或独立真实捕获spot。

## 下一步单个Windows只读动作

```powershell
Get-Content -LiteralPath "D:\Research\STdeconv_benchmark\run_tangram_seqfishplus_5fold.py" -Raw
```

预期输出Python源代码。若文件不存在/输出截断，不修改其它文件，返回实际错误；然后从现有代码决定是否可以batch整合。
