// English edition based on resume-zhixing.typ. Save to update the PDF in VS Code.
#let ink = rgb("#20252b")
#let accent = rgb("#B45A14")
#set document(title: "Wantai Zhang | AI Agent / Backend Development", author: "Wantai Zhang")
#set page(paper: "a4", margin: (top: 10mm, bottom: 10mm, left: 13mm, right: 12mm), numbering: none, fill: white)
#set text(font: ("Times New Roman", "Kaiti SC"), size: 11pt, fill: ink, lang: "en")
#set par(justify: true, leading: 0.45em, spacing: 0pt)
#let title(t) = block(width: 100%, above: 6pt, below: 4pt, sticky: true)[
  #stack(dir: ttb, spacing: 3pt,
    text(size: 12.5pt, weight: "bold", fill: accent)[#t],
    line(length: 100%, stroke: 0.65pt + accent),
  )
]
#let item(body) = block(above: 0pt, below: 5pt)[#grid(columns: (5pt, 1fr), column-gutter: 3pt, [•], body)]
#let entry(t, date: "") = block(below: 4pt)[#grid(columns: (1fr, auto), column-gutter: 6pt,
  text(weight: "bold")[#t], text(size: 9.5pt)[#date])]
#grid(columns: (18mm, 1fr, 18mm), column-gutter: 2mm, align: top,
  [],
  align(center)[
    #v(3mm, weak: false)
    #text(size: 22pt, weight: "bold")[Wantai Zhang]
    #v(5pt, weak: false)
    #text(size: 9.5pt)[☎️ +86 17706023481 | 📮 #link("mailto:17706023481@163.com")[17706023481\@163.com]]
    #v(3pt, weak: false)
    #text(size: 10pt)[📖 AI Agent / Backend Development Intern]
  ],
  image("assets/photo.jpg", width: 18mm),
)

#title[EDUCATION]
#entry(date: "Sep 2025 – Jun 2028 (Expected)")[Xiamen University | Master of Applied Statistics]
GPA: *3.9/4.0; Top 2%*
#v(4pt, weak: false)
#entry(date: "Sep 2021 – Jun 2025")[Xiamen University | Bachelor's in Data Science and Big Data Technology]
GPA: *3.6/4.0; Top 20%*
#v(4pt, weak: false)
*Honors:* *National Scholarship*; University Scholarship; First-Class Academic Scholarship; Liangwen Scholarship, Department of Statistics.

#title[INTERNSHIP EXPERIENCE]
#entry(date: "Aug 2026 – Present")[#box(baseline: -1pt, image("assets/hello-logo.png", height: 10pt))#h(3pt)Hello (Shanghai Hello Puhui Technology Co., Ltd.)]
*AI Agent Development Intern*
#v(3pt, weak: false)
*Context:* Customer-service agent platform for carpooling and battery-swapping services, covering multi-turn workflows, tool integration, hotline responses, and complaint escalation.
#v(4pt, weak: false)
#item[*Workflow and state management:* Addressed skipped workflow stages and stale context after order changes using *AgentScope, intent recognition, and an FSM* for evidence collection, liability assessment, negotiation, and resolution. Stored state in *Redis*, blocked progression on tool failure, reset order context, and checked versions before writeback. Supported approximately *19,700 / 2,700 daily agent-handled conversations*, respectively.]
#item[*Tools and human oversight:* Prefetched business data for initial responses and exposed specialist agents as tools. Used *Hooks and HITL approval* to pause sensitive operations and resume after approval. Following platform rollout, concurrent chats per representative rose from *5 to 20*; *96.6% / 88.7%* of agent-handled conversations required no human takeover.]
#item[*Hotline response and concurrency:* Used *Reactor* to prepare routing, special-intent detection, and bridging responses concurrently; streamed bridging text before the main reply via *Spring MVC SseEmitter*. Isolated model-stream reads from tool RPCs, bounded concurrency with *Java 21 virtual threads, semaphores, and permit-acquisition timeouts*, and canceled remaining tasks after hang-up or human transfer.]
#item[*Complaint escalation:* Combined contact frequency, prior external complaints, and related tickets with *LLM-based escalation detection*. Routed qualifying cases to specialist agents and linked follow-up tickets. After overall platform rollout, dissatisfaction rates for fully agent-handled conversations fell from *32.6% to 25.9%* (carpooling) and *35.6% to 27.8%* (battery swapping).]

#title[PROJECT EXPERIENCE]
#entry(date: "Jun 2026 – Aug 2026")[◆ Zhixing | Intelligent Travel Assistant]
*Context:* A multi-city travel agent integrating fragmented destination, transport, and accommodation information, with multi-turn planning, preference memory, and itinerary updates.
#v(4pt, weak: false)
#item[*Planning and memory:* Used a *single agent and state machine* for seven stages: requirements, destinations, transport, accommodation, dining, itinerary, and budget. Exposed tools by stage; rolled back and invalidated downstream results after requirement changes. Used *PostgreSQL Checkpointer / Store* for session recovery and cross-session preference updates.]
#item[*Two-layer intent routing:* Combined *rule-based gates and structured LLM routing* for direct queries, automatic confirmation, and step-by-step confirmation. Used conversation history to resolve short replies and missing details, preventing weather or timetable queries from advancing the planning workflow.]
#item[*Retrieval and context:* Indexed *71 guides across 39 cities* into *654 parent / 3,120 child chunks*. Combined *BM25, vector retrieval, multi-query expansion, and LLM reranking*, restored parent context, and cached results by version in Redis. On *18 fixed entity-retrieval queries*, *Recall\@3 improved from 87.96% to 95.37%; MRR\@3 from 0.676 to 0.787*.]
#item[*Evaluation and safeguards:* Integrated *DeepEval, a Qwen judge, and GEval* with positive/negative calibration samples and asynchronous answer checks. Used *requirement versions and idempotent receipts* to reject stale cards and duplicate confirmations. Passed *120 regression tests and 27 targeted API checks* covering routing, disconnection, user isolation, and restart recovery.]

#title[TECHNICAL SKILLS]
#item[*Backend:* Python, SQL, FastAPI; HTTP, authentication, asynchronous tasks; familiarity with Java thread pools and bounded concurrency.]
#item[*Agents and evaluation:* LangChain / LangGraph, MCP, Function Calling; orchestration, context and memory management; DeepEval / GEval and regression-based evaluation.]
#item[*RAG:* Parsing, chunking, embeddings, hybrid retrieval, RRF, reranking; Milvus / pgvector; incremental indexing, parent–child retrieval, citations, and access filtering.]
#item[*Data and engineering:* PostgreSQL, MongoDB, Redis; transactions, indexes, caching, idempotency, retries; Docker, log-based debugging, and Codex-assisted development.]
