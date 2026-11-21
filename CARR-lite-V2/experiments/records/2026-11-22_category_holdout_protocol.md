# CARR-lite V2 严格类别留出：计划与实验状态（2026-11-22）

## 源头与研究目的

- 来源：用户提供的 Claude 原八项扩充计划，第 4 项：B01–B04 共享同类目标细胞，逐基础场景留出仍可能存在兄弟场景共现；应增加稳定（stable）/中等参考（medium）/易混淆（confusable）/低参考（lowref）**整个类别留出**的敏感性分析。
- 用户明确不补充空间预测点位图；不扩充与原计划无关的展示工作。
- **状态：SCRIPT_COMMITTED_NOT_RUN**。已提交独立脚本 `CARR-lite-V2/experiments/category_holdout_carr_v2.py`；未获得用户 Windows 干跑或训练日志，不得报告任何本实验结果。

## 协议（拟执行）

- 13 base → 4 类：stable B01–B04（4 base ×4 深度 = 16 views）；medium B05–B07（3 base ×4 =12）；confusable B08–B10（12）；lowref B11–B13（12）。
- 4 折：一次留出整类所有 base/深度，训练使用其他三类，所有测试视图保持互斥。52 views 总计评估一次，`Original_${method}`、`AbundanceOnly`、`HGBC_a15`、`HGBC_a30`、`HGBC_a50` 各 52 行，预期每基础方法 260 行，不是 52 个独立样本。
- 复用 `cross_method_carr_v2.py` 的 `make_dataset`、`apply_models`、`validate_prediction` 及旧版 train_fold/evaluate，不改算法本体。不同基础方法独立训练，**不是零样本跨方法迁移**。
- 新脚本允许 `--method RCTD|CARD`，可选 `--ablation no_depth` 用于不使用已知测序深度特征的敏感性比较；默认保留已知深度，仅可用于受控模拟实验。
- 独立输出目录；如果非空则直接报错拒绝覆盖；Dry-run 严格检查输入与类别划分而不写文件。
- 该验证比逐 base 留出更严格，**仍不是独立真实数据泛化验证**。测试真值只用于评估，原始参考独立性等要按后续审计核查。

## 下一步唯一人工操作

首先手动同步 GitHub 最新 `main` 到 `D:\Research\st-deconvolution-research`，确认成功后再给单条 RCTD dry-run 命令。

- 目的：准备下一项原计划的严格类别留出，不启动训练。
- 接受条件：PowerShell 执行 `git pull --ff-only` 成功或者已是最新，并可见本脚本。
- 后续依次：RCTD dry-run → RCTD 正式运行 → CARD dry-run → CARD 正式运行 → 逐类均值对比 → 简单校准基线。
