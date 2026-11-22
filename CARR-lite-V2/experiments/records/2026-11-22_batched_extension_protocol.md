# 2026-11-22 两篇 SCI 扩充：批处理执行协议（代码已提交、Windows 尚未运行）

## 用户最新决定

- 先按 Claude 已提供的两篇原始补实验清单推进，**研究审计集中留到实验扩充结束后交给 Claude 做**。最基本输入校验、目录防覆盖、固定测试拆分属于正常实验执行要求，不是当下重开全面审计。
- **写脚本时尽量打包多个预定义任务，一次人工运行完成多组实验；但仍由研究者亲自在 Windows 执行，每轮向用户仅发一条 PowerShell 指令并等待日志**。
- 不再插入额外空间预测spot图。所有真实/模拟结果、负结果、计划与已运行分开记录。
- 文献/外部数据新增需求留在后续批次，不得将脚本提交写成实验已完成。

## 已创建：CARR-lite V2 一键批处理（待Windows预检/运行）

- [批处理调度器](../carr_pending_experiments_batch.py)
- [新增简单替代实验](../logistic_threshold_category_holdout.py)
- 复用仓库既有 [四类别严格留出实现](../category_holdout_carr_v2.py) 和训练、评价模块，不另造CARR模型。
- 固定 **RCTD、CARD两种基础方法**；每个方法执行：
  1. \`marker_k=20\`（相对标准40改变一项）
  2. \`marker_k=80\`
  3. \`confusion_k=1\`（相对标准3改变一项）
  4. \`confusion_k=5\`
  5. \`no_depth\` 特征消融，严格四类别留出重新拟合
  6. 简单控制 \`LogisticPresence12\`（StandardScaler+class-balanced LogisticRegression C=1；目标存在概率×**训练集阳性真值均值**）和 \`Threshold1D\`（原预测阈值固定0.005、不调参）。
- **总计12个新运行任务**（六任务×两个基础反卷积器）；前四项固定单参数改变，不把测试结果用于后验选择最佳marker/confusion设置。
- 参照旧严格类别留出：\`D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1\{RCTD,CARD}\metrics_by_scenario.csv\`，用于校验基线存在，但不会重跑旧full/a30或已有ridge/iso。
- 单个敏感性或no_depth新结果：\`260\`行（52模拟视图×Original/AbundanceOnly/a15/a30/a50五个输出），共10任务；单个Logistic/Threshold新结果：\`156\`行（52×Original/Logistic/Threshold），共2任务。**预期总行数=2912**，不是2912独立样本。
- 每个任务单独输出路径到 \`D:\Research\STdeconv_benchmark\results\CARRliteV2_pending_batch_20261122_v1\{job}\{method}\`，no_depth再增子目录；任务完整才可跳过，残缺结果停止并保留，绝不无条件覆盖。
- 每任务写log（\`logs/*.log\`），调度器记录实际完整流水线wall time（含构造特征、训练、预测、评价、写文件，不等于独立模型的纯预测速度）及 \`batch_metric_means.csv\` 和 \`batch_run_status.csv\`。保存原始失败日志、不要挑选性删掉不利超参数。
- 数据为13个相关base×4个模拟深度，四类group-heldout，不是生物学独立重复；已知深度特征只适用模拟协议。
- **代码状态：GitHub 已提交；仅在本工具运行环境作 Python 语法编译检查及调度器12任务构造/输出路径唯一性基础烟测。未在用户Windows真实输入上dry-run，更未训练。**
- 用户先本地\`git pull --ff-only\`，回传实际终端结果；之后一条命令 \`python "D:\Research\st-deconvolution-research\CARR-lite-V2\experiments\carr_pending_experiments_batch.py" --dry-run\`；通过后另给 \`--run\`。可用 \`--tasks sensitivity,no_depth,controls\` 子集，但用户当前意图是一次完成整组。

## 已创建：CTW-RF Stacking 敏感性批处理（同样尚未运行）

- [CTW批处理脚本](../../CTW-RF/experiments/ctw_stacking_sensitivity_batch.py)
- 复用已有 \`global_stacking_cv.py\` 的 \`load_inputs\`、归一化、5折划分、SLSQP权重求解、JSD/RMSE计算；**只针对全局 stacking comparator，不是CTW-RF Proposed_CV重训**。
- 预定义 **3个spot级CV种子×3种候选池(2/4/6法)×4种训练calibration spot预算(100/200/500/all)=36种配置、共180次五折内求权重**。训练折抽取calibration spots，测试折不参与拟合。small pool是此前结果启发的探索性池，不可包装成独立最优模型筛选。
- 结果输出到 \`D:\Research\STdeconv_benchmark\results\CTWRF_stacking_sensitivity_20261122_v1\`：\`metrics_by_seed_pool_budget.csv\`、\`metrics_by_fold.csv\`、\`weights_by_fold.csv\`、\`descriptive_means_across_seeds.csv\`、\`run_config.json\`；如果个别优化失败会记录 \`failed_configurations.csv\`，不虚称36配置全部完成。不会覆盖已有非空目录。
- 该批次后仍需CTW-RF Proposed_CV同fold比较、最近邻EnDecon及新数据/独立单位评估；本批仅推进原计划随机拆分、校准集规模和候选池敏感性。
- **代码状态：GitHub已提交。语法本地静态检查与单配置mock smoke test通过；Windows真实输入/36配置都未运行。**
- 先CARR，后CTW，用户每次一条PowerShell指令；每阶段运行完按本机原始CSV汇总分析。

## 当前下一步唯一用户动作（不训练）

在Windows PowerShell同步这3个新脚本：

\`\`\`powershell
git -c http.proxy=http://127.0.0.1:7897 -C "D:\Research\st-deconvolution-research" pull --ff-only
\`\`\`

- 预期Git pull显示新增3个python脚本和本协议文档；不等于已运行。
- 失败时完整报错贴回，不重复clone、不用\`git reset --hard\`。
- 下一轮先给CARR \`--dry-run\` 检查，随后再一次 \`--run\` 实际批处理。用户明确希望减少单个实验反复人工点击，调度器已做12任务自动队列和断点保护。
