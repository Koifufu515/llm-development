# 知行旅行助手

基于原教程逐步实现并适配的本地Agent应用。实际目录：`/Users/jarvis/Desktop/大模型开发/knowgo-travel`。

## 启动与使用

双击 `启动后端.command` 启动Colima、PostgreSQL及后端。完整页面：<http://127.0.0.1:8001/studio>；状态学习页：<http://127.0.0.1:8001/learn>；接口文档：<http://127.0.0.1:8001/docs>。

完整页面可填写单城/多城与停留天数，选择自动参考方案或手选交通，观察SSE阶段进度、逐日安排、预算、候选与来源。可以保存偏好、新建会话、读取历史计划，或在对话入口直接查询、修改与继续讨论。

这是监听127.0.0.1的本机演示。用户UUID用于偏好命名空间，不代表生产身份认证。写请求当前串行保护状态，不宣称已支持生产多用户并发。

## 配置

`.env` 保留本地数据库和原DeepSeek配置。`外部服务配置.env` 保存Qwen、高德、腾讯、Variflight和AIGOHOTEL凭证，仅本机使用、600权限、版本控制忽略。切换 `MODEL_PROVIDER=qwen` 后新模型请求即读取Qwen配置。Qwen地域须与百炼Key一致。切换凭证后远程MCP按凭证指纹重新发现工具；日志和报告不写Key。

默认Qwen模型为qwen-plus（非思考）；保留DeepSeek适配。RAG使用本地BGE-small-zh-v1.5，无需付费embedding Key。模型权重在data/models，向量索引在data/rag_index，均不纳入版本控制。

## 实现结构

- `app/main.py`：应用生命周期、会话/聊天接口、checkpoint读取；兼容原学习页。
- `app/core/state.py`、`transitions.py`、`middleware.py`：结构化需求、版本确认、修改回退及工具执行守卫。
- `app/core/checkpointer.py`、`store.py`：PostgreSQL短期checkpoint与长期偏好/业务记录，namespace隔离。
- `app/tools/completion_tools.py`：偏好保存、明确选票、行程生成、酒店/航班/驾车只读工具。
- `app/services/contracts.py`：多城输入、逐日输出与预算参数校验。
- `app/services/planning.py`：采集、检索、生成、结构校验、预算与阶段事件；fast与sequential参考通道。
- `app/services/knowledge.py`：中文BGE、BM25、RRF、父块引用、城市过滤、词项覆盖率重排与TTL/LRU缓存。
- `app/services/routing.py`：模型三通道路由及明确的固定关键词参考基线。
- `app/services/remote.py`：商业MCP、酒店字段归一、航班时刻、高德与腾讯驾车。
- `app/api/delivery.py`：完整规划/SSE、手选与幂等提交、长期偏好、历史计划、直查与外部服务状态。
- `scripts/patch_rail_mcp.py`：12306-mcp 0.3.10跨日上车日期修正，启动自动应用。npm恢复后也需应用。

## 数据与边界

高铁余票来自真实12306 MCP；天气来自Open-Meteo（已有stdio MCP）或高德；酒店来自AIGOHOTEL；航班时刻来自Variflight。接口成功与空结果、缺凭证、格式异常分开处理。腾讯地图实测曾返回121日配额耗尽，见报告，不将其记成成功。

交通候选保留实际站名；城市范围查询包含远郊站，须检查是否方便。生成内容不能引用未选车次；自动选择是参考方案，不执行购买。酒店只有报价明确且距供应商查询中心10公里以内才自动选，否则提供候选/区域与预算估算。酒店和餐饮估算、未知费用与实时参考价分别标注；儿童票按成人参考价估算，无年龄信息时不虚构优惠；默认不包含返程、门票和市内交通。

知识库目前为10份UNESCO来源的人工中文摘要、23父段，是可扩展的检索实现与小规模评测语料，不代表覆盖全国旅行攻略。嵌入真实运行；当前重排为词项覆盖率，未使用cross-encoder。此次重排没有改善Recall/MRR，不能包装成提升。

sequential是本项目用于实验的“串行采集+逐日生成”参考实现，fast是“并行采集+集中生成”；不是历史线上系统对比。输出JSON校验和车次校验不等于人工全面评估行程合理性。现阶段不是任意交通方式都能自动闭环：多城自动规划默认高铁；航班、自驾已提供实际查询入口，需要根据实际场景单独使用。

## 验证与指标复跑

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/verify_delivery_live.py
.venv/bin/python scripts/verify_acceptance.py
.venv/bin/python scripts/benchmark_quality.py
.venv/bin/python scripts/benchmark_performance.py rail planning tokens
```

真实调用会使用本机模型/服务额度。基准单独运行，测量时不要同时修改代码或提交其他规划请求；默认每种性能通道3轮，Token输入对照各2轮。原始记录在reports，报告口径与简历正文也在该目录。失败记录保留，不以成功个例替代全部结果。

手工标注的32路由/23检索用例适用于回归观察，未经用户独立标注审核，不外推线上准确率。原先40项回归是历史阶段数据；本轮结果以最近命令与报告为准。助手验证与用户掌握分别记录，后续复盘仍覆盖原61项题目及追问。

## 来源

原始资料：用户提供《知行旅行助手-v2》《知行旅行助手代码-v2》《知行旅行助手八股-v2》。外部数据：12306/Open-Meteo/高德/Variflight/AIGOHOTEL；知识资料归属与链接保留在data/guides。适配代码与原教程的改动包括Qwen/DeepSeek切换、本地中文BGE、现有需求版本守卫以及精简页面。
