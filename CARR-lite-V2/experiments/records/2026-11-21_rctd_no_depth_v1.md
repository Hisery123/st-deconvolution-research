# CARR-lite V2 × RCTD：No-depth 特征消融（运行记录）

- 日期：2026-11-21
- 证据等级：**RUN_LOG_CONFIRMED**（用户粘贴 Windows PowerShell 终端输出；原始结果 CSV 尚未提交或独立读取）
- 配置：`--method RCTD --ablation no_depth`，排除 `depth_fraction` 特征。
- 输入：13 个基础场景 × 4 个测序深度 = 52 场景视图。
- 源脚本：[`cross_method_carr_v2.py`](../cross_method_carr_v2.py)，特征消融功能引入提交 `f5e3ead23bb122027a5c333d35021f283c2fddac`。
- 预定输出目录：`D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_depth`。

## 输入验证（用户返回）

```text
INPUT CHECK PASS: RCTD 52 scenario views
ABLATION: no_depth excluded columns: ['depth_fraction']
DRY RUN PASS — no files written
```

## 正式执行（用户返回日志末尾）

```text
Completed B12_lowref_ref70_depth_100
Completed B12_lowref_ref70_depth_050
Completed B12_lowref_ref70_depth_025
Completed B12_lowref_ref70_depth_010
Completed B13_lowref_bg8_depth_100
Completed B13_lowref_bg8_depth_050
Completed B13_lowref_bg8_depth_025
Completed B13_lowref_bg8_depth_010
FINISHED 260 result rows
OUTPUT D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\RCTD\no_depth
```

## 证据解释和下一步

- 日志确认 RCTD no_depth 分支完成 52 场景、260 条结果，**不代表性能上升或下降**。
- 本次的完整输出指标 `metrics_by_scenario.csv` 未上传，尚未与 RCTD 非消融运行结果做数值比较。
- 下一步：CARD `--ablation no_depth --dry-run`，通过后正式运行 CARD no_depth；之后把两种基础方法在同一个 HGBC 配置（建议预先固定 a30）下对齐比较 target_RMSE、target_MAE、balanced_AUPRC、recall 等。
- 不将四种测序深度视作四个独立生物学重复，不覆盖已完成的主实验。
