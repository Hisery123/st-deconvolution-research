# CARR-lite V2 预注册对照：简单后校准基线（2026-11-22）

## 目的（对应 Claude 原八项计划第 6 项）

检验 CARR-lite V2 在多基础方法下的改善是否仅由一个简单、同样有监督的校准器即可获得；如果简单方法在同样评测协议下匹配或超过其核心指标，应如实收窄方法主张。

## 研究设计

- 评价数据：原有 RCTD/CARD 在52个模拟场景视图的预测，每法13个基础场景×4测序深度；采用已经运行完成的 **stable / medium / confusable / lowref 四折整类别留出**。
- 训练/测试协议与 `category_holdout_carr_v2.py` 一致，保留相同的 `confusion_k=3`、`marker_k=40`，相同的基础预测与特征构造，同样的 `apply_local_correction`/ `set_local_target` 组成约束与 `v1.evaluate` 五项指标。各基础方法独立训练校准器。
- **固定简单基线**（不以测试折结果调参）：
  1. `Ridge12`：12个相同输入特征（包含受控模拟中的 `depth_fraction`），`StandardScaler + Ridge(alpha=1.0)`，拟合 `delta=true_target-base_target`，沿用原有 local projection。
  2. `Isotonic1D`：仅使用原始 `base_target` 一维输入，`IsotonicRegression(increasing=True, out_of_bounds="clip", y_min=0, y_max=1)` 拟合 `true_target`，沿用同一个 local projection。
  3. 输出 `Original_RCTD/CARD` 作为评估种子/口径对齐检查，不属于额外训练方法。
- 每法52视图×3输出=156行，两个方法合计预计312行；**都是模拟视图，不是312独立生物重复**。
- 现有严格留出 `HGBC_a30`、`AbundanceOnly` 由 `CARRliteV2_category_holdout_20261122_v1` 既有结果比较，不重新训练，以相同 `scenario_id`、`method` 配对。
- 平衡AUPRC的评估种子采用和严格类别留出原实验一致的 `seed + 100*fold + depth`，使同一视图评价可比。
- 已知深度特征只在受控模拟中可用；`Ridge12` 的 default 包含它，Isotonic1D 不使用。后续真实部署须检查无深度输入结果，不能借已知受控下采样比例宣称实际可部署。

## 实施状态

- [CODE_COMMITTED_NOT_RUN] 脚本 [`simple_calibration_category_holdout.py`](../simple_calibration_category_holdout.py) 已提交 GitHub main，commit `2b198ecbfdab0a4eba0827ba8ed07c88ed62a67d`。未在用户 Windows 上同步或干跑；不得宣称训练完成。
- [NEXT_SINGLE_ACTION] 研究者 PowerShell 手动 `git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only`；取得成功日志后才给 RCTD `--dry-run` 的下一条命令。不得直接正式运行。
- 所有结果输出到新的 `D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1\{RCTD,CARD}`，遇非空目标目录拒绝覆盖。

## 证据判据

- *改善*必须先说明指标，如 Target RMSE 越低越好，AUPRC、Recall 越高越好，不能因一个指标改善就宣称全面性能提升。
- **比较务必看 CARD**：严格类别留出下当前 CARR HGBC_a30 已观察到 CARD Balanced AUPRC 和 Recall 均低于原版；简单基线是否更好是关键风险，不能省略。
- 先对每个基础场景汇总四个深度，再统计13个场景上的差值、方向数量；FOV/供体级外部验证仍需额外数据。
