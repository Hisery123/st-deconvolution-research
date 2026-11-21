# CARR-lite V2 × CARD no_residual：已存在完整规模输出的目录检查

- 日期：2026-11-21。
- 证据类型：**USER_CONSOLE_DIR_CHECK**（仅用户 PowerShell 本地目录及行数，不代表独立读取原始 CSV）。
- 用户尝试运行 `--method CARD --ablation no_residual --out-dir D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1`，脚本先输出 `INPUT CHECK PASS: CARD 52 scenario views` 与 `ABLATION: no_residual excluded columns: ['residual_projection', 'residual_marker_mean']`，然后因目标目录非空而触发 `FileExistsError`；本次尝试**没有重新完成训练**。
- 研究者随后只读检查目标目录 `D:\Research\STdeconv_benchmark\results\CARRliteV2_ablation_20261121_v1\CARD\no_residual`，得到：
  - 场景子目录数：52；
  - `metrics_by_scenario.csv` 的 CSV 记录数：260；文件大小 43226 字节；Windows 修改时间 2026/11/21 18:48:48；
  - `run_config.json` 存在；文件大小 14006 字节，修改时间 2026/11/21 18:48:48。
- 证据解释：输出数量与完成的 52 场景×5 配置一致，且存在运行配置。**当前是已存在的完整规模输出，而非本次重新运行成功日志。** 尚未核对 JSON 内容、每场景方法构成或指标数值，因此不提前声称结果验证完成或效果改善。
- 下一步：用**一条只读命令**确认 run_config 里的 `method/ablation`，并比较 RCTD/CARD Full、No-depth、No-residual 的 `HGBC_a30` 指标。
