# 2026-11-22 CARR-lite V2 与简单后校准基线：13 个 base 配对分析（模拟场景）

## 数据与核查状态
- **USER_WINDOWS_STDOUT**：用户本地用 pandas 只读合并严格四类别留出 CARR 以及 Ridge12/Isotonic1D 指标 CSV。
- 用户输出 `BASE PAIR CHECK PASS: 26 method-base units`：RCTD、CARD 各13个基础模拟场景，按 `base_method, held_out_base, method` 分组，每组先对4档受控深度平均。
- 此处仅归档用户终端给出的配对改善数与均值差；未收到原始逐场景 CSV、未独立复算、未计算独立生物重复显著性。严格优于用严格不等式，持平未计入改善数量。
- `HGBC_a30` 是本次预设固定版本，不因为测试结果选择其他 `a`。

## 原始用户终端汇总

```csv
base_method,versus,RMSE_wins,AUPRC_wins,delta_RMSE,delta_AUPRC
RCTD,Ridge12,8,11,-0.000755,0.009002
RCTD,Isotonic1D,6,9,-0.000846,0.015575
RCTD,AbundanceOnly,6,7,0.000078,0.000832
CARD,Ridge12,6,5,0.000174,0.001379
CARD,Isotonic1D,6,8,-0.000185,-0.003185
CARD,AbundanceOnly,4,7,-0.000082,0.000312
```

- `delta_RMSE = HGBC_a30 - comparator`，越负越利于 CARR。
- `delta_AUPRC = HGBC_a30 - comparator`，越正越利于 CARR。

## 限定性解释

- **RCTD**：相较Ridge12，CARR在8/13 base上Target RMSE更低，在11/13 base上AUPRC更高，总体均值方向也有利；与Isotonic1D相比，Target RMSE虽平均更低，但只在6/13 base严格获胜，不能宣称大多数场景定量性能更好。
- **RCTD AbundanceOnly**：CARR总体Target RMSE平均略高（+0.000078），只在6/13 base的RMSE获胜；AUPRC微小提升但仅7/13胜出。三分支融合的必要性没有获得所有指标支持。
- **CARD**：对Ridge12，CARR在6/13 base RMSE获胜，在5/13 base AUPRC获胜；RMSE均值变差（+0.000174），AUPRC均值略升（+0.001379），存在方向权衡。对Isotonic1D，CARR的RMSE平均略好（−0.000185）但只有6/13 base获胜；AUPRC平均较差（−0.003185），尽管8/13 base获胜，说明少数场景损失可能较大。对AbundanceOnly，RMSE只4/13胜出，平均略好（−0.000082），需要报告。
- 这些皆是模拟场景及受控深度下的描述性敏感性结果，**不是13个独立FOV/供体**，没有统计显著性，也不能证明机制创新性。
- 早先已验证：严格类别留出下 Original_CARD 的AUPRC/Recall高于包括 CARR 在内的校准方法，属必须保留的负结果。不得只报告目标RMSE。

## 研究决策与下一项

- Claude原计划第6项中已完成Ridge12和Isotonic1D两类简单替代的同协议模拟评估（`logistic`/阈值类其他基线**尚未完成**，如要声称第6项全部做完须标注局限）。
- 不再因为当前结果不利就后验变更HGBC参数或重挑最佳对照。
- 下一项优先转入Claude原计划的**真实数据/独立FOV与参考隔离核查**（第2/3项），先定位已有逐FOV真实评估CSV和代码，不立即重跑。不补空间预测点位图。
