# 原方案核对事实

- 用户新要求：以原方案为基准，原有能力必须保留，不接受简化替换。仅排除Windows专用兼容处理，数据全部保留。
- 上轮代码已有运行能力，但缺原文Agent真实astream_events流式/清洗/折叠/reset、酒店评分择优、原正文规范化、原离线6样本及多项匹配口径基准；不能仅用73项测试称完整。
- 已核对原文第12章行7538–7645：首轮缓冲、后续实时推、协议清洗、跨轮重述折叠、四出口、buffer_all/defer_push。当前app/full.chat仍agent.ainvoke，只有plain是真实token流。
- 原文声称9个MCP源，但最终配置代码块0672-993ad2ab4f7b实际列7项：weather/search/amap/12306/Variflight/hotel/bailian；geng-weather和geng-search-image在叙述列出，当前已见最终配置未包含。需继续核对其来源地址/配置，不能凭“9”字样伪造两个连通服务。
- Tavily自建stdio search_server尚未接入；用户此前配置的Key只有百炼/高德/腾讯/Variflight/AIGOHOTEL，没有已知TavilyKey。不输出任何实际凭证。
- 原文0593完整_stream_agent95行已读取；原文代码在stream.push同步无界队列，但安全取消与有界背压可保留成明确兼容修复，不能损失事件行为。

最终源码优先于过时叙述：0526-af025f844781的快速通道最终实现bind_tools+ainvoke结构化，再由0530的_push_rendered分段渲染；并非“快速通道必须逐模型token吐正文”。先前助手称其缺真实token流过于笼统，需要按最终代码恢复分段渲染，与Agent的astream_events分开标注。0526有back_text变量却传back的原代码bug，应修成back_text并保留全部归一功能。最终0708_stream_agent与0593代码一致，未提供live_first_round参数，叙述中的该分支不作为已存在源码虚构。

原文规则版本冲突已核对：0507同一代码块先首站固定1、后有缩进错误的“平均分配”备选；代码文档终版0695明确首站1天，其余均分；0299住宿窗口末站封顶末日以N-1晚计。忠实模式采用0695+0299，保留显式city_days覆盖且修复一日0晚，不把备选均分当唯一原文规则。原文酒店hotel_rank实际使用AIGOHOTEL.starRating，属于供应商星级/等级，不是用户点评分，不能宣传“用户评分4.5”；恢复该排序函数且如实标注字段含义。
