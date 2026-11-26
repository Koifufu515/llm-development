# 原方案功能矩阵（55组）

源代码块共709个去重块；分组不是函数覆盖率。每组保留原块号、当前实现、证据和边界。私有材料与外部报价不可得不假称原样取得；Windows唯一用户排除。

| ID | 功能 | 当前实现 | 验收/边界 |
|---|---|---|---|
|01|环境/uv/Docker/macOS|`README.md`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`环境验证.json`|
|02|PG Checkpointer短期记忆与thread恢复|`app/core/checkpointer.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-restart.json`|
|03|PG Store独立用户namespace|`app/core/store.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|04|UserProfile/TravelHistory/Record/住宿预算|`app/full/memory.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|05|单create_agent+StepConfig动态工具/Prompt|`app/full/agent.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|06|七步前向9工具与前置依赖|`app/full/agent.py`、`app/full/completion_tools.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|07|通用回退+7别名+级联清理|`app/full/agent.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|08|同轮多个状态Command冲突阻断|`app/full/agent.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`tests/test_full_integrity.py`|
|09|五类记忆工具及本次/长期区分|`app/full/agent.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|10|9类MCP功能/7类原终版配置|`app/mcp_core/client.py`|原私有天气/图片端点缺失，以功能等价自建stdio替代；九服务发现成功，不等于每个接口每条分支均已真实通过。 证据：`reports/reference-final-acceptance.json`|
|11|MCP隔离加载/重名/失效重建|`app/mcp_core/client.py`、`app/services/remote.py`|隔离加载与重建实现；九源发现和工具回归验证，不声称对每一家供应商都做了断网恢复压测。 证据：`reports/reference-final-acceptance.json`|
|12|车票别名/ContextVar/注册守卫同对象|`app/full/rail_guard.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`tests/test_reference_toolnode.py`|
|13|车票12行裁剪与原载荷口径|`app/full/rail_guard.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-rail-benchmark.json`|
|14|12306上车日/跨日/席别可售|`app/core/rail.py`、`scripts/patch_rail_mcp.py`|包含本轮之前真实上车日期补丁验收；跨日/席别等以回归覆盖，非全部线路外部验证。 证据：`reports/full_final_live.json`|
|15|多机场航班与同航班票价融合|`app/full/capabilities.py`、`app/services/remote.py`|多机场时刻真实成功；同航班号票价融合实现，当前有效报价不可得，未知价保持None，未声称有价分支真实成功。 证据：`reports/full_multi_airport.json`|
|16|高德驾车/坐标与油费估算区分|`app/full/capabilities.py`|高德驾车真实成功；油费是0.65元/公里参考估算；腾讯配额失败未计成功。 证据：`reports/full_final_live.json`|
|17|航班结构缺失降高铁/临时故障不误判无机场|`app/full/workflow.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`tests/test_full_regressions.py`|
|18|否定识别/裸词交通改选/旧卡失效|`app/full/transport_switch.py`、`app/full/workflow.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|19|四类多段卡片/逐段逐城手选|`app/full/capabilities.py`、`app/full/selection_tools.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|20|酒店共享rank规则/异常价格/品牌降级|`app/full/hotel_rank.py`、`app/full/capabilities.py`|沿原rank规则；供应商starRating实际为酒店等级，不冒充旅客评分。 证据：`tests/test_reference_selection.py`|
|21|城市顺序/首站1日/日期同源/N-1晚|`app/full/domain.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`tests/test_full_domain.py`|
|22|本地游0交通/一日0住宿|`app/full/workflow.py`、`app/full/domain.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`tests/test_full_domain.py`|
|23|目的地分类Send并行/reducer/合成|`app/full/destination.py`|真实三天全流程覆盖子图；不是逐条对所有目的地分类都做完真实验证。 证据：`reports/reference-flow-final.json`|
|24|高德主天气+备用/日期不冒充/关联行程|`app/full/weather.py`、`app/full/plans.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-providers-live.json`|
|25|图片独立MCP搜索/地图缺图补图|`app/mcp_core/servers/image_server.py`、`app/full/plans.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|26|父1000/200子200/50/持久Chroma1536d|`app/full/knowledge.py`|71份历史英文攻略、39城、404025字符；不是原作者私有数据库，3120子块索引真实存在。 证据：`data/full_rag/manifest.json`|
|27|中文BM25/Dense/RRF0.4+0.6|`app/full/knowledge.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-rag-cold-warm.json`|
|28|MultiQuery/HyDE/改写/组合|`app/full/knowledge.py`|四策略均有实现；冷/热真实基准使用MultiQuery，未分别测四种策略的泛化收益。 证据：`tests/test_full_regressions.py`|
|29|0-10相关评分/9到6到3/长上下文重排|`app/full/knowledge.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-rag-cold-warm.json`|
|30|完整Redis缓存/模型配置与语料版本隔离|`app/full/knowledge.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-rag-cold-warm.json`|
|31|342城市选择与Redis缓存|`app/full/api.py`、`app/full/cities.json`|城市目录和Redis实现；342是选择器，不是攻略或可实时服务覆盖率。 证据：`reports/reference-final-acceptance.json`|
|32|统一意图词表/三通道/补槽位上下文|`app/full/intents.py`、`app/full/routing.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-router-after.json`|
|33|结构化路由及技能目录/历史短答|`app/full/reference_router.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-router-after.json`|
|34|表单0模型接收/完整需求聊天抽取|`app/full/api.py`、`app/full/agent.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-first-frame.json`|
|35|自动选城/多城天数扩展并告知|`app/full/workflow.py`、`app/full/domain.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`tests/test_reference_express.py`|
|36|Express并行收集与按偏好选择|`app/full/workflow.py`、`app/full/capabilities.py`|各3轮六次均完成；仍有模型错误和重试，不宣称线上成功率或稳定延迟。 证据：`reports/reference-flow-final.json`|
|37|原正文60字/缺日/空时段/末日返程归一|`app/full/reference_itinerary.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`tests/test_reference_normalization.py`|
|38|结构化生成失败退标准Agent|`app/full/workflow.py`、`app/full/agent.py`|真实Graph/工具/PG故障注入，模型协议/地图回放原真实产物；不是一次新的真实Qwen故障演练。 证据：`reports/reference-faults.json`|
|39|预算数量/人数/间夜/票价明细/估算分离|`app/full/domain.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|40|八事件/队列/close哨兵/断连释放|`app/full/events.py`、`app/full/api.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|41|真实Agent token/首轮缓冲/四出口/清洗reset|`app/full/streaming.py`|真实Qwen工具轮token验证与四出口回归；结构化计划是先验证后代码分块，不冒称逐token生成。 证据：`reports/reference-stream-live.json`|
|42|原48字符代码渲染块/0.025秒|`app/full/streaming.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`tests/test_reference_streaming.py`|
|43|用户名邮箱/JWT/bcrypt/注册登录/所有权|`app/full/security.py`、`app/full/api.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|44|ORM会话消息CRUD/软删/历史原文与摘要|`app/full/api.py`、`app/full/database.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|45|多份历史计划/同版本幂等/原四层契约|`app/full/database.py`、`app/full/legacy_contract.py`|实现存在，按所列专项证据及120项回归验收；不表示穷尽所有输入或线上流量。 证据：`reports/reference-final-acceptance.json`|
|46|地图真实POI/坐标转换/路线/图片|`app/full/plans.py`、`app/static/travel.html`|真实页面发现博物馆误配停车场，先两项红灯后修复，通过真实高德主体查询并修合成账号地图；真实主体查询已通过，最终截图另附。 证据：`reports/reference-map-probe.json`|
|47|界面登录/需求/会话/手选/偏好/计划历史|`app/static/travel.html`|功能重建前端，非原作者缺失的React仓库；用户名登录/地图/餐饮多选/交通顺序/重命名归档恢复均浏览器验证。 证据：`reports/reference-browser.json`|
|48|原三维GEval/0.5/异步在线/不阻断|`app/full/reference_quality.py`、`app/full/quality.py`|原三维0.5阈值，同语义固定步骤；六样本两轮仍有作者正样本被判低，不当作事实审计。 证据：`reports/reference-six-cases-stable.json`|
|49|原六条同构正反边界/两轮/失败保留|`evaluation/itinerary_cases.py`、`scripts/evaluate_reference.py`|原动态步骤失败保留；固定步骤结果另存，未更改样本或阈值凑100%。 证据：`reports/reference-six-cases.json`|
|50|确定性RouterMetric与全部原路由样本|`evaluation/router_metric.py`、`evaluation/router_cases.py`|原21条同集回归20/21；曾用此集调整提示词，不是独立测试集；仍有一例缺技能。 证据：`reports/reference-router-after.json`|
|51|同条件串并行/裁剪/完整RAG/状态机vsExpress|`scripts/benchmark_reference_flows.py`|铁路/RAG各3轮与完整流程各3轮分开；流程基准生成/查询冻结，后修POI展示单独复验；全部早期超时保留。 证据：`reports/reference-flow-final.json`|
|52|首业务帧与首文本分开计时|`scripts/benchmark_reference_first_frame.py`|各3轮首业务帧，不是TTFT；主动断连后6/6后续写入成功。 证据：`reports/reference-first-frame.json`|
|53|故障注入/DB质量断言/重启隔离|`scripts/accept_reference.py`|重启校验Checkpoint/Store/2历史版本SHA；故障回放范围见独立report，不冒充生产事故。 证据：`reports/reference-restart.json`|
|54|Windows兼容排除（用户明确）|`README.md`|仅Windows事件循环兼容按用户明确排除；没有因此删除任何业务或数据库数据。 证据：`excluded-user`|
|55|来源差异/指标口径/部署脚本/打包与复盘|`README.md`|原文差异/指标/面经填空/部署与脱敏交付另附；61条用户实操未记为已完成。 证据：`reports/原方案复现对照.md`|
