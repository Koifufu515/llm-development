#set document(title: "爱学习 Agent 开发｜面试复盘")
#let accent = rgb("#B45A14")
#let ink = rgb("#20252b")
#set page(paper: "a4", margin: (x: 26mm, top: 21mm, bottom: 21mm), numbering: "1")
#set text(font: ("Times New Roman", "Kaiti SC"), size: 14pt, fill: ink, lang: "zh")
#set par(justify: false, leading: .95em, spacing: 18pt)
#set heading(numbering: none)
#set list(spacing: 5pt)
#show heading.where(level: 1): it => block(width: 100%, sticky: true, above: 16pt, below: 11pt)[
  #text(size: 20pt, weight: "bold", fill: accent, it.body)
  #v(3pt)
  #line(length: 100%, stroke: .65pt + accent)
]
#show heading.where(level: 2): it => block(sticky: true, above: 23pt, below: 12pt,
  text(size: 17pt, weight: "bold", it.body))

#let followups = block(sticky: true, below: 5pt)[*追问*]

#block(sticky: true, below: 8pt)[
  #text(size: 22pt, weight: "bold", fill: accent)[爱学习 Agent 开发｜面试复盘]
]

= 一、实习介绍与客服 Agent <part-1>

== 1. 请先做一下自我介绍。

== 2. 请讲一下你在哈啰实习期间做的事情。

== 3. 你们的客服系统是 Multi-Agent 架构吗？底层用的是什么框架？

#followups
- 用的是 LangGraph、Deep Agents，还是其他框架？
- 业务路由 Agent 怎么把工作交给具体的业务处理 Agent？

#block(sticky: true, below: 5pt)[*复盘补答：为什么选 AgentScope Java？*]

我理解这个选型最主要的考虑是 *Java 生态兼容性*。哈啰现有后端基于 Spring 和 Java，AgentScope Java 可以直接嵌入已有服务。如果接入主要面向 Python 和 TypeScript 的 LangGraph，还要处理跨语言集成，工程成本可能更高。

另一个考虑是 *框架抽象和业务流程能对应上*。Agent 和 Message 支持路由 Agent 与业务 Agent 协作，Tool 对应业务工具调用，Hook 则能承接人工审批所需的拦截点。

== 4. 你们的 Skill 是怎么加载的？

#followups
- 一个 Skill 有哪些内容？除了具体任务内容，还有什么结构？

== 5. 你们是怎么管理多轮会话上下文的？

#followups
- 你们是通过不同的 Agent 隔离上下文吗？

== 6. 你们使用的是什么模型？有没有降级机制？

#followups
- 用的是千问的哪个版本？只有这一个模型吗？
- 如果线上模型出了问题怎么办？遇到过 429 吗？当时怎么解决？

== 7. 简历里写的 AgentScope 是什么？它在项目里承担什么角色？

#followups
- 你了解 Handoff 吗？面试官举的例子是路由 Agent 将会话控制权交给业务处理 Agent。

== 8. 你们的口碑分析工作流是怎么取数的？

#followups
- MCP 和 CLI 有什么区别？

= 二、状态管理、开发工具与人工审批 <part-2>

== 9. 你们是怎么避免 Agent 跳步的？

#followups
- 为什么把业务状态存到 Redis，而不是 MongoDB？
- 什么叫跳步？能举个具体例子吗？

== 10. 为什么切换订单后，旧订单的信息还可能影响新订单？

#followups
- 这和上下文有什么关系？Redis 里具体存了什么？
- 会话状态和订单上下文是怎么拆分的？
- 切单后哪些信息必须重置，哪些可以保留？保留工具调用记录的目的是什么？

== 11. 你怎么理解 Agent 的上下文管理？你们用的框架上下文窗口有多大？

== 12. 你平时用什么工具开发？

#followups
- Cursor 的上下文窗口有多大？主要用哪个模型开发？

== 13. 你了解 LangGraph 的 Checkpointer 吗？它能覆盖你们 Redis 这一层的功能吗？

== 14. 人工审批用的是框架自带的生命周期机制，还是你们自己加的拦截点？

#followups
- 为什么用 Hook？
- 审批通过和不通过分别怎么处理？

== 15. 你们系统里正在运行的 Agent 有多少个？可以怎么分类？

#followups
- 风险条件满足后由其他 Agent 接管，这一段有用到 Workflow 吗？
- 审批通过后，是让一个 Agent 执行，还是把整个流程交给它？

== 16. 你们线上的误退款率是多少？

#followups
- 刚才提到的八九千元退款金额，都是换电和顺风车业务产生的吗？

= 三、模型与热线响应 <part-3>

== 17. 主 Agent 和申诉话术 Agent 分别用的是什么模型？

#followups
- 如果把现在用的模型换成明显更弱的模型，你会怎么办？
- 你听说过 Harness 吗？

== 18. 你们有统计热线 SSE 流式输出的首 Token 时间吗？

#followups
- 从用户体感看，用户提问后大概要等多久才能收到 Agent 的输出？

== 19. 承接话术是怎么生成的？

#followups
- 是用固定模板、检索后生成，还是直接由模型生成？
- 怎么避免承接话术和最终办理结论矛盾？

= 四、外投风险识别与评测 <part-4>

== 20. 通过 LLM 识别会话里的监管或媒体投诉倾向，这部分是你设计的吗？具体是怎么做的？

#followups
- 你们的 Prompt 是一版就成型的吗？
- 你们说的外投具体是什么？是外部投诉吗？

== 21. 有没有把普通用户诉求误判成高风险的情况？

#followups
- 现在误判有减少吗？Precision 是什么意思？

== 22. 你们怎么知道业务办理效果变好了？

#followups
- 最终看的是哪个指标？除外投率外，有没有考虑人工处理成本等指标？
- 会定期回看 Agent 处理的工单吗？人工会重新审核高风险判断吗？
- 离线评测数据集还会补充吗？

= 五、知行智能旅行助手 <part-5>

== 23. 为什么想自己做一个智能旅行助手？

#followups
- 有试过 Workbot、Muse 或豆包小豆这类 Personal Agent 吗？
- 为什么选择自己动手做？直接用 ChatGPT 可以吗？

== 24. 知行项目为什么使用 RAG？为什么不直接通过飞书文档、CLI 或 MCP 获取资料？

#followups
- 这个项目现在还在用吗？

== 25. 你做的 Agent 评测具体是做什么的？

#followups
- 项目已经用到了多种 Agent 能力，为什么还需要额外做评测？

= 六、面试结束前的交流 <part-6>

== 26. Cursor 现在还能调用第三方模型吗？

#followups
- 你怎么看待最近推出的新模型？
- 你用过 Gemini 新出的几个模型吗？
