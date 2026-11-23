# 2026-11-23 seqFISH+ Tangram五折调用器源码已收到：核心runner依赖识别

## 证据级别

[USER_PASTED_SOURCE] 用户在Windows终端只读打印`D:\Research\STdeconv_benchmark\run_tangram_seqfishplus_5fold.py`完整源代码并粘贴。当前仅为用户所贴源码，没有在Windows运行新流程。当前GitHub研究库`main`全树检索没有`run_tangram_self_benchmark.py`文件。

## 当前代码可验证内容

- 该文件是**five-FOV外层调度器**而不是Tangram建模主体。默认实际映射程序为`D:\Research\STdeconv_benchmark\methods\Tangram\run_tangram_self_benchmark.py`，真实空间评价程序为`D:\Research\STdeconv_benchmark\evaluation & visualization\evaluate_seqfishplus_real_spatial.py`。
- 每个fold目录`held_out_FOV*`中检查预测`predictions\Tangram_self_benchmark.csv`是否存在；若有效并无`--force`则跳过旧预测；新运行核心命令`python run_tangram_self_benchmark.py --base_dir <fold> --seed 0 --num_epochs 500 --mode cells --density_prior rna_count_based --device auto --max_genes 3000`。
- `prediction_is_valid`将CSV与`pseudo_spot_ground_truth.csv`比较行列shape、spot ID集合、type列集合、NA，**使用真值文件仅做旧输出结构校验；不直接证明核心训练时不读取真值，必须读核心runner代码**。
- 默认汇总和日志会写入既有fold/原始`batch_runs\Tangram`目录；如果为新参考合成数据运行，必须采用新独立目录，避免强制覆盖旧结果。
- 新CARR参考单细胞训练伪spot→留出目标FOV实验仍未运行。既有CARR五折runner训练用其它FOV已知标签，不是reference-only训练。

## 阻断的唯一接口

必须核实核心`methods\Tangram\run_tangram_self_benchmark.py`实际读取的文件、输入生成时的基因/参考与样本细胞协议、是否使用`pseudo_spot_ground_truth`不恰当、模型输入形式与训练输出格式、结果目录保护。此核心文件在当前GitHub研究库没有同步，不能仅凭外层wrapper就编造其内部数据契约、伪造训练伪spot的Tangram预测。

## 下一步Windows一条只读命令

```powershell
Get-Content -LiteralPath "D:\Research\STdeconv_benchmark\methods\Tangram\run_tangram_self_benchmark.py" -Raw
```

预期打印Tangram基础预测模型真实源码；若不存在或终端输出被截断，返回原报错，可用本地上传`.py`（不修改原数据）。完成后直接编排5个FOV及固定训练伪spot预算的可复用批处理，不再要求重复提交已收到runner。
