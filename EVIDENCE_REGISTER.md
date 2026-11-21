# EVIDENCE_REGISTER — 论文证据索引

更新：2026-11-21。状态：**仓库基础审计，尚未进行原始实验复算**。

## 证据等级

- D0 = 直接读取的原始代码、日志、CSV 与真实重算；
- D1 = 直接读取的稿件，只能证明“稿件如此报告”；
- D2 = 第三方 AI 审查摘要，未复核其声称读到的路径/实验；
- D3 = 计划与假设，尚无实验支持。

D0/D1 不等同于独立生物学验证；需另行核查单位与划分。

## 当前记录

| 编号 | 研究线 | 来源 | 本次所见事实 | 证据等级 | 核查要求 |
|---|---|---|---|---|---|
| CTW-M1 | CTW-RF | `CTW_RF_ICBBS2026_intro_reorganized.tex` | 426 行英文稿；报告 cortex-SVZ 2000 pseudo-spots / 19 类 / 五折、aggregate RMSE 0.724 | D1 | 逐折真值、预测、脚本和参考细胞 ID |
| CTW-M2 | CTW-RF | 同上 | 稿件将 DLPFC 0.298 称为参考伪 spot 的 aggregate RMSE，不是真实 Visium 比例真值 | D1 | 训练/评估隔离和指标定义 |
| CTW-C1 | CTW-RF | Claude 转述审查 `粘贴的文本 (1)(20261121-020404).txt` | 提醒参考泄漏与最近邻集成工作风险 | D2 | 原始脚本、文献原文、方法实现核对 |
| CARR-M1 | CARR-lite V2 | `CARR-lite_V2_Method_Paper_Chinese(5).tex` | 201 行精简稿；描述 52 场景/5 FOV/70 聚合 spot | D1 | 来源表、split IDs、每个 FOV 结果 |
| CARR-M2 | CARR-lite V2 | 同上 | 报告 rare-positive RMSE 0.035965→0.016277、singleton AUPRC 0.239072→0.334900 | D1 | 原始 CSV 复算、指标/汇总口径 |
| CARR-M3 | CARR-lite V2 | 同上 | 文稿对受控深度使用已知深度比例作为特征 | D1 | 检查实际特征工程/部署可用性 |
| CARR-C1 | CARR-lite V2 | Claude 转述审查 | 推荐 RCTD/CARD 扩展、严格划分、FOV 级统计 | D2 | 脚本、结果文件及实际分组元数据 |
| CTW-X1 | CTW-RF | 待设计 | 全局 stacking vs CTW-RF vs 最近邻融合 | D3 | 先查近邻原文、数据公平、预算 |
| CARR-X1 | CARR-lite V2 | 待设计 | RCTD/CARD + CARR | D3 | 先检查基础预测矩阵的行列、归一化、校准器训练 |

## 已直接核查稿件的完整性标识（SHA-256）

- CTW: `802cf84f0de39bb843de467b1d7a03b252b96623e145142ed4f421b217ea51f7`。
- CARR: `8b079ccf0a47344d90cc5620615166534a51a42d3bd1164524a58f5002fff3fc`。

**此索引不提供原稿的仓库下载地址：原文尚未上传到本公共仓库。**

## 待补证据登记规范

每次后续运行须登记：commit / 脚本路径 / 输入数据 hash / sample_id / 参考细胞 ID / split ID / 实验参数 / seed / CSV 路径 / 指标公式 / 独立单位 / 是否已复算 / 失败情况。

不得只凭模型评分或 AI 表述将 D1/D2 升级为 D0。
