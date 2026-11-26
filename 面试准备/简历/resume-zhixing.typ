// 正式简历：沿用已确认的 test 排版；修改后保存可自动导出同名 PDF。
#let body-size = 10.5pt
#let leading = 0.5em
#let accent = rgb("#B45A14")
#let ink = rgb("#20252b")
#set document(title: "张万泰｜Agent开发实习简历", author: "张万泰")
#set page(paper: "a4", margin: (top: 12mm, bottom: 10mm, left: 13mm, right: 12mm), numbering: none,
  fill: white)
#set text(font: ("Times New Roman", "Kaiti SC"), size: body-size, fill: ink, lang: "zh", tracking: 0.15pt)
#set par(justify: true, first-line-indent: 0pt, leading: leading, spacing: 0pt)
// 轻描边增强重点文字的显示效果。
#show strong: it => text(weight: "bold", stroke: 0.10pt + ink, it.body)
// 新模板的棕色栏目标题与横线；分开布局，避免负间距造成重叠。
#let title(t, top-space: 6pt) = block(width: 100%, above: top-space, below: 5pt,
  inset: (x: 9pt), sticky: true)[
  #stack(dir: ttb, spacing: 4pt,
    text(size: 14pt, weight: "bold", fill: accent)[#t],
    line(length: 100%, stroke: 0.65pt + accent),
  )
]
// 正文无卡片：去掉白底、描边和圆角，仅保留排版间距。
#let card(body) = block(width: 100%, fill: none, stroke: none,
  inset: (x: 9pt, y: 0pt), above: 0pt, below: 0pt, breakable: true, body)
#let item(body) = block(above: 0pt, below: 8pt)[#grid(columns: (6pt, 1fr), column-gutter: 3pt, [•], body)]
#let entry(t, date: "", font-size: 10.5pt) = block(below: 6pt)[#grid(columns: (1fr, auto), column-gutter: 7pt,
  text(size: font-size, weight: "bold")[#t], text(size: 9pt)[#date])]

// 左右等宽占位，使姓名与联系方式相对整页居中，照片位于右上角。
#block(inset: (x: 9pt), above: 0pt, below: 0pt)[
  #grid(
    columns: (18mm, 1fr, 18mm),
    column-gutter: 2mm,
    align: top,
    [],
    [
      #align(center)[
        #v(4mm, weak: false)
        #text(size: 22pt, weight: "bold")[张万泰]
        #v(8pt, weak: false)
        #text(size: 10pt, tracking: 0pt)[#box[☎️：17706023481#h(3pt)｜#h(3pt)📮：#link("mailto:17706023481@163.com")[17706023481\@163.com]#h(3pt)｜#h(3pt)📖：Agent开发/后端开发]]
      ]
    ],
    image("assets/photo.jpg", width: 18mm),
  )
]

#title(top-space: 0pt)[教育经历]
#card[
  #grid(columns: (1fr, auto), [*厦门大学*｜应用统计｜硕士｜GPA：*3.9/4.0*（专业前2%）], [2025.09—2028.06])
  #v(8pt, weak: false)
  #grid(columns: (1fr, auto), [*厦门大学*｜数据科学与大数据技术｜本科｜GPA：*3.6/4.0*（专业前20%）], [2021.09—2025.06])
  #v(8pt, weak: false)
  *荣誉奖项：* *国家奖学金*、校级奖学金、学业一等奖学金、统计系良文奖学金。
]
#title[实习经历]
#card[
  #entry(date: "2026.08—至今")[#box(baseline: -1.5pt, image("assets/hello-logo.png", height: 11pt))#h(4pt)*上海哈啰普惠科技有限公司*｜AI Agent开发实习生]
  *业务背景：*面向顺风车、小哈换电等客服场景，参与 AI 客服托管系统建设，完善多轮业务办理、工具调用、热线响应与风险识别能力，提高复杂客服问题的处理效率。
  #v(6pt, weak: false)
  #item[*多轮业务编排与状态管理：*针对订单争议处理中 *Agent 流程跳步、切换订单后沿用旧记录*的问题，基于 *AgentScope*，结合*意图识别与有限状态机（FSM）*控制“取证—判责—协商—处置”业务流程；通过 *Redis 保存会话状态与订单上下文*，工具失败时暂停推进，切单后重置相关上下文，并在*回写前校验版本，防止过期请求覆盖新进度*，支撑顺风车、换电日均约 *1.97 万、2,700 条*托管会话。]
  #item[*工具调用与人工协同：*针对客服首轮回复依赖多次业务查询、敏感操作需要人工审批的问题，通过*工具预调用*提前获取业务数据，减少模型等待查询结果的时间；将专项子 Agent 封装为工具处理特定任务，基于 *Hook 实现 HITL 人工审批*，在敏感工具执行前暂停，审批通过后恢复会话继续办理。平台上线后，坐席并发接待由 *1v5 提升至 1v20*，两条业务线托管后未由人工接管的比例分别为 *96.6%、88.7%*。]
  #item[*热线响应与并发优化：*针对热线多步处理等待较长、慢工具调用拖累其他请求的问题，通过 *Reactor 并行执行*业务路由、特殊意图识别和承接话术生成，正常业务先播放承接话术，再输出正式回复；基于 *Spring MVC 的 SseEmitter* 流式输出，采用*专用线程池隔离模型流读取与工具调用*，结合 *Java 21 虚拟线程、信号量及获取许可超时*控制模型读取并发，并在用户挂断或转人工后取消后续任务，减少资源争抢和无效回复。]
  #item[*外投风险识别与工单联动：*结合进线次数、历史外投和同单工单等信息，通过 *LLM 分析会话中的监管、媒体投诉倾向*，满足风险接管条件后交由*专属 Agent 接管并关联工单跟进*，完善高风险诉求处理路径。平台整体上线后，顺风车、换电全托管不满意率分别由 *32.6% 降至 25.9%*、*35.6% 降至 27.8%*。]
]

#title[项目经历]
#card[
  #entry(font-size: 10.5pt, date: "2026.06—2026.08")[◆ 知行｜智能旅行助手]
  *项目背景：*面向多城旅游用户，针对攻略、交通与住宿信息分散，以及需求变更后行程难以同步调整的问题，构建支持*多轮沟通、偏好记忆和行程生成*的旅行助手。
  #v(6pt, weak: false)
  #item[*多轮规划与偏好记忆：*针对用户分轮补充需求、修改目的地后旧方案仍被沿用的问题，采用*单 Agent＋状态机*串联需求、目的地、交通、住宿、餐饮、行程及预算七步流程，按阶段提供工具；需求变更后*回退至对应步骤，清除下游旧结果*，通过 *PG Checkpointer / Store* 恢复会话并保存偏好，支持用户跨会话沿用、新增或修改出行偏好。]
  #item[*两层意图识别：*针对天气、班次查询被带入完整规划，以及“确认”“换一个”等短回答依赖上文的问题，设计*规则门禁＋结构化模型路由*，将请求分为单点直查、自动确认与逐步确认三条通道；规则可判定的请求直接分流，其余交由模型结合历史消息识别意图、补齐信息，避免简单查询误推进规划流程。]
  #item[*知识检索与上下文优化：*针对景点信息召回不稳、整篇攻略输入过长的问题，将 *71 份攻略、39 城内容*划分为 *654 个父块、3,120 个子块*，通过 *BM25＋向量混合检索、多查询扩展与 LLM 重排*筛选相关片段，再补充父块上下文，以 *Redis 版本缓存*减少重复检索；在 *18 条冻结实体检索题*上，*Recall\@3 从 87.96% 提升至 95.37%，MRR\@3 从 0.676 提升至 0.787*。]
  #item[*Agent 评测与异常保障：*针对回答质量缺少持续检查的问题，接入 *DeepEval＋Qwen 裁判＋GEval*，先用离线正反样本校准裁判，再对落库后的回答异步质检；通过*需求版本校验与幂等回执*拦截旧卡片和重复确认，避免覆盖当前行程状态。建立并通过 *120 项回归测试、27 项专项 API 检查*，覆盖路由、断连、跨用户隔离及重启恢复等场景。]
]

#title[专业技能]
#card[
  #item[*编程与后端：*熟悉 *Python、SQL*，具备 FastAPI 接口开发、数据处理及问题排查经验；理解 HTTP、身份鉴权和异步任务处理，了解 Java 线程池与有界并发。]
  #item[*Agent 开发与评测：*具备 *LangChain / LangGraph、MCP、Function Calling* 项目实践，理解意图识别、任务编排、上下文管理与短期/长期记忆；使用 *DeepEval / GEval* 和固定回归题集评估回答质量、定位失败场景。]
  #item[*RAG 与检索优化：*具备 *文档解析与切分、Embedding、混合检索、RRF、Rerank* 实践，使用 Milvus、pgvector 等向量存储；理解增量索引、父子块扩展、引用溯源及文档权限过滤。]
  #item[*数据库与工程实践：*使用 *PostgreSQL、MongoDB、Redis* 完成数据持久化、缓存和异步作业处理，理解事务、索引、幂等与失败重试；具备 *Docker 部署、日志排查*经验，使用 Codex 辅助开发与调试。]
]
