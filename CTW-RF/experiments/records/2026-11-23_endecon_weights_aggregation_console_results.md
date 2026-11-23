# 2026-11-23 EnDecon三方法池：本地CSV读取的真实权重、简单聚合、收敛指标

## 证据

[USER_WINDOWS_CSV_SUMMARY] 研究者在Windows本机只读：
- `D:\Research\STdeconv_benchmark\results\CTWRF_EnDecon_aggregation_20261122_v1\endecon_weights_by_pool.csv`
- 同目录 `ensemble_metrics_by_pool.csv`
- 同目录 `endecon_diagnostics_by_pool.csv`
并粘贴全量关键列。以下逐项转录用户提供的输出，并非助手已直接得到三个原始CSV字节。

## 全部方法权重

| pool | method | weight |
|---|---|---:|
| strong2 | CARD | 0.119203 |
| strong2 | cell2location | 0.880797 |
| expanded4 | CARD | 0.480304 |
| expanded4 | cell2location | 0.287698 |
| expanded4 | RCTD | 0.117074 |
| expanded4 | SPOTlight | 0.114924 |
| full6 | Tangram | 0.128667 |
| full6 | RCTD | 0.228215 |
| full6 | CellDART | 0.102428 |
| full6 | CARD | 0.194867 |
| full6 | cell2location | 0.149918 |
| full6 | SPOTlight | 0.195905 |

**直接算法解释**：strong2中cell2location权重大于0.5；对仅两个基线预测的每个spot×celltype，加权中位数的最终输出选择cell2location的数值（相同值情况下亦一致），因此`EnDecon_weighted_median`的JSD复现cell2location单方法基线0.098996；这不是两方法共同有效集成的额外收益。两方法等权坐标中位数与平均数相同，为实现所预期。full6最大权重仅0.228215，集成输出来自不同基线的坐标中位数，权重未聚焦某一强方法。

## 同池三类无监督聚合指标

| pool | method | JSD | matrix_RMSE |
|---|---|---:|---:|
| strong2 | EnDecon_weighted_median | 0.098996 | 0.056752 |
| strong2 | coordinate_median | 0.107527 | 0.053225 |
| strong2 | equal_mean | 0.107527 | 0.053225 |
| expanded4 | EnDecon_weighted_median | 0.119340 | 0.051988 |
| expanded4 | coordinate_median | 0.136323 | 0.055314 |
| expanded4 | equal_mean | 0.140022 | 0.052325 |
| full6 | EnDecon_weighted_median | 0.233707 | 0.073754 |
| full6 | coordinate_median | 0.216576 | 0.070923 |
| full6 | equal_mean | 0.160047 | 0.058340 |

**观测结论**：在full6池，本Python移植版EnDecon JSD 0.233707与RMSE 0.073754均比坐标中位数0.216576/0.070923与等权均值0.160047/0.058340更差。**合理但尚未验证的机制解释**：不一致且质量参差的基础方法占有较分散的方法权重，逐坐标中位数易丢失强预测法的优势；需基于逐celltype预测与逐spot误差才能验证，不能直接宣称算法普遍不鲁棒。

## 迭代诊断

| pool | lambda | iterations | converged | aggregate_runtime_seconds |
|---|---:|---:|---|---:|
| strong2 | 347.666312 | 3 | True | 0.007847 |
| expanded4 | 1120.917586 | 3 | True | 0.016886 |
| full6 | 1384.482916 | 3 | True | 0.022876 |

收敛仅为本移植版目标函数达到代码定义的终止准则，不等于已在R作者包数值复验；运行时间仅为融合聚合计算，不包含基础反卷积模型训练。

## 进一步跨研究对照

既有CTW SoftOpt三seed均值：
- strong2 JSD .114850 / matrixRMSE .052449；EnDecon strong2 JSD优而RMSE不优。
- expanded4 .110677/.044521；full6 .101723/.041453；此两池CTW两指标均优于Python EnDecon移植版。
- **不同监督信息**：CTW使用训练折真值估计细胞类型特异性权重，EnDecon移植版通过所有预测数据的无监督transductive方式估计全局方法权重。此为既有基础预测的算法聚合比较，不代表原作者完整EnDecon软件经原文协议复现；同一个2000spot基准，也非跨供体验证。
- E4_GITHUB_URL=https://github.com/Hisery123/st-clustering-research/tree/main/experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE 曾和本次控制台日志一并出现，属于用户另一`st-clustering-research`仓库路径，本次CTW/CARR结果不可与该E4实验混为一谈。

## 下一个阶段

用户坚持先做完原定增量补实验，最后集中交Claude科学审计。CARR真实空间FOV已有`D:\Research\STdeconv_benchmark\run_carr_lite_v2_seqfishplus_5fold.py`，但该runner及构建器目前在用户Windows本地，未收入GitHub当前研究仓库`CARR-lite-V2/experiments`；在未读当前runner源码前不能臆造scRNA-only reference训练→held-out target部署脚本参数。下一条Windows命令应只读输出该runner源码（或上传文件），以便批量复用、避免重复训练。该实验**尚未执行**。
