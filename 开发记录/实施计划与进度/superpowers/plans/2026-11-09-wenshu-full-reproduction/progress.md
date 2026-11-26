# 进度
2026-11-09 用户授权完整复现并完成后再停止。已应用writing-plans/文件规划，建立独立计划，复制无真实.env/运行数据/依赖的工作区实施副本。当前只读了技术方案1—200行及旧部署/审计说明，剩余正文待逐段核对。

三份Markdown已全文读完；HTML全文441行按范围逐段读取（初次过长输出后已补读75—450），模板数值未视作本机证据。原231文件比对只有.gitignore与Chat.tsx两项原文件变更，新增本机部署脚本保留。59项离线基线通过。Worker实际已因Redis TimeoutError退出；Milvus backend在原代码未实现、build_vector_store静默返回Memory。将作为先修缺陷做红/绿与真实服务验收。

## 首批实现
- 检索5项先失败后通过：禁止真实向量失败混入hash、维度/条数校验、重排按index回排、未知backend拒收、持久正文部门二次校验。新增真实Milvus HNSW适配，保留原后端。
- 队列3项先失败后通过，新增持久租约/CAS、heartbeat、重试退避、DLQ与过期Worker写回隔离；上传按job ingestion_key幂等并保留文件至终态。现有enqueue回执finish兼容同一消费者。首轮完整68项通过；真实Redis kill/重试实验尚待做。
- 原数据库已备份：28集合、7文34块，保存在桌面.local/backups/20261109-before-full/database.json（600权限），旧配置与变更文件也备份。禁止打入交付包。
- Docker旧实例仅3GB/2CPU，因此新建独立colima-wenshu 6GB/3CPU，不重启旧实例，--activate=false不改默认上下文；官方kubectl1.35 SHA校验后安装工作区.tools/bin。独立K3s1.35节点Ready；Milvus2.6.9镜像正在下载。
- 初次本地测试路径误拼导致文件不存在，已修正；初次启动Colima缺kubectl，补官方客户端后正常；原测试finish传enqueue回执与新lease协议不符，已限同消费者兼容，未去掉回归断言。

### 接续执行：真实检索与权限边界
- 用户已明确授权：仅7份样例的脱敏文本可发送百炼；原件本地保留。Python/pi双出站脱敏已接线，82项姓名/学号映射，34块扫描无已知标识残留。
- 真实 text-embedding-v4 /1024维 + qwen3-rerank + Milvus 连通，7文档重建完成；Milvus count=35，而源chunk合计34，尚需排查多出的测试向量，不把35称为业务块数。
- 独立文枢Colima/K3s/Milvus健康；本机Mongo/Redis/pi/API/Worker/前端运行。知行/QuarryVM未改。
- 真实Redis作业领取进程kill(-9)后租约接管、ACK归零、3次失败DLQ通过。独立UUID测试队列，无业务队列消费。
- 扫描PDF本机中文OCR实测通过，保留原子表格/Markdown fence/页码回归。
- 新增服务器身份覆盖模型角色、会话原子归属（Mongo唯一主键）、旧会话归属迁移、删除墓碑；检索候选在重排前回填正文并校验active/部门，Embedding故障降BM25不伪造hash，多query并发。
- Verifier非法结构与语义服务故障改为不通过，最多两次重写后只返回官方原文。
- 最新离线回归91项通过（2秒级）；这是测试回归，非真实问答准确率。最新边界修改仍在staging，待同步与真实验收。
- 整体49项矩阵未全部验收，不能称完整复现完成；继续Loop治理、真实问答、生命周期、部署观测和固定集评测。

### 接续：治理、真实流式与运行边界
- 最新完整离线回归114项通过，前端与pi生产构建通过。新增测试见test_session_boundaries、test_mutable_scope、test_document_governance、test_stream_contract、test_usage_isolation、test_governed_cache、test_distributed_budget。
- 新增治理工作台：策略审核/驳回、跨部门冲突协调与双方确认、术语审核、文档版本与有效期、通知。前端生产构建通过；浏览器交互尚待验收。
- Mutable Scope按原方案限制：新Prompt本体、Hook动作、规则正文需人工审核；自动调参需同已生效本体、回放通过、阶段/置信度满足。pi保存产物仅能进pending，不可旁路发布。
- Skill Miner改为近7天、>=20条且成功率<80%筛选；修复DBSCAN距离负浮点。Skill可实际执行已审核校历lookup并保存来源，缺校历不编造日期；沙箱执行相同工具路径。
- 真实SSE已打通Python→pi→Qwen逐增量，前端区分未校验草稿与正式result；断连取消任务，pi Agent.abort释放请求。每轮模型usage用ContextVar隔离，未知金额null，Trace与实验outcome写入时延/usage。
- 真实问答第一条天气问题73.443秒，校验3次失败后退官方原文，保留reports/real-qa-first.json；发现Verifier参考条款被截500字且引用编号不同于Answer，已改用相同完整证据/编号及仅核对问题所需信息。
- 真实SSE明确骑行问题：阶段首帧0.064s、模型首增量5.05s、整轮6.824s，校验通过。仅单条结果，不是全量准确率/P95。reports/real-sse.json。
- Redis两实例12并发、用户限额3，恰好放行3；真实pi250ms超时在0.286s返回502，activeExecutions归0。reports/live-boundaries.json。
- Milvus Strong查询逻辑34行，与Mongo active34块完全一致，无孤立向量；此前stats35是物理统计不可当业务行数，已澄清。
- 新增模型签名Embedding LRU、身份/记忆/策略/文档版本签名的Redis答案缓存，命中后仍回查active官方chunk。真实冷热性能对照尚待做。
- Worker每日幂等maintenance/Loop、过期提醒/记忆保留，文档重建先成功Embedding再删旧向量；自动免审不再伪造accuracy=1。文档生命周期/术语/冲突有离线回归，真实多角色API+页面仍待验收。
- 未完成：知识缺口工单与聚类、Thompson Sampling和合并拆分执行、全面部门预算/治理范围审查、独立部门服务、Docker全栈、Helm/HPA与HA监控、分层冻结评测/两轮Loop对照、1→20Pod负载、浏览器多角色验收、独立恢复与最终包。49项不能整体标完成。


### 用户再次要求连续完成后的进展
- 新增知识缺口聚类/部门工单，绑定已生效官方资料才能关闭；参数优化采用版本隔离Thompson Sampling及固定会话分配，反馈只计原执行样本一次。灰度/参数实验期间绕过答案缓存，防止污染对照。
- 发现旧切分器标题只入path而正文遗漏，已保留标题正文；截图较多PDF增加整页OCR。7文档已生成新版本，旧7版本和原件保留。当前active33块，全部版本67块；不能继续复用旧34块统计。
- 包含姓名学号的答辩分组名单access_roles=admin；在重排和最终回填前校验角色，学生不能召回名单。已加回归。
- 最新119项离线回归通过；独立Python3.11容器断网运行同119项也通过。原测试59项，不以新增测试数量冒充项目完整度。
- 三类镜像已构建，独立Compose六服务健康。恢复7部门/14文档/67块/5术语，7个active重建独立Milvus集合，原DB不变，不复制用户账号/会话。reports/compose-restore.json。
- Compose应用层验收后暂停以节省专用6GB VM内存，Mongo/Redis数据卷保留；原本机3000/8000等服务未停止。
- 24题冻结输入回归（21正例+3无依据），第一轮BM25/RRF/重排Hit@5=1，MRR=.97619/.93810/1；关键点覆盖=1，Verifier通过20/24，拒答3/3。0标注错误/0运行错误。保存frozen-evaluation.json，不是独立人工QA准确率。该题集用于修复，不能再称盲测。
- 失败3例为模型把表格序号误作来源编号，另1拒答被裁判过度要求解释；已加入针对引用编号/问题范围/正确拒答的明确提示，待8条独立合成裁判边界样本校准及同输入重测。保留第一轮结果。
- 新增Mongo3副本+Redis3副本/Sentinel，私有凭证均在.local/config，源文件无真实值。Mongo内部key最初URL-safe Base64不被接受，已轮换为标准Base64，旧值失效，3副本及初始化Job已成功。不要输出任何Mongo认证错误原文（可能回显内部key）。
- 官方Helm4.0.0下载SHA256通过，Helm lint通过；Chart补模型/真实向量/Sentinel/隐私挂载/前端/部门探针。
- 新增JSON日志、请求TraceID、HTTP/模型/检索/Loop OTel spans，观测栈Prometheus/Grafana/Loki/Promtail/Tempo/Collector配置已生成，待实际部署与验收。
- 发现专用K3s继承HTTP代理但无NO_PROXY导致kubectl logs EOF，正持久化专用profile和systemd drop-in并重启K3s；仅wenshu profile，不动knowgo。
- 未完成：裁判校准和两轮Loop证据、真实多角色/页面验收、K8s应用安装/数据恢复/HA故障注入/观测/HPA1→20与负载、成本口径、独立恢复包和最终矩阵。继续执行，不得阶段性结束。


### 接续：集群/Loop/容量与真实失败
- Kubernetes根服务、zfxy/hqaq两部门Agent、pi、Worker、前端全部Ready；Prometheus/Grafana/Loki/Promtail/Tempo/Collector已真实启动。Prometheus抓取3个业务Pod为up=1，自定义metrics API能返回部门inflight，HPA正常读取0/8。
- K3s NO_PROXY修复已生效，kubectl logs/port-forward恢复。专用集群Mongo3/Redis3均Ready，独立库wenshu_k8s恢复7部门/14版本/67块，active33向量；随机验收账号仅存在该库，未复制原账号。
- 真实两轮Loop脚本已完成：第一轮格式反馈→pending规则→模拟审核→真实Qwen后续回答包含三个指定标题；第二轮20条明确标注的脚本错误回放→真实Embedding聚类→候选Skill→20题沙箱，候选得分.28所以保持pending，未强行上线。reports/loop-live-proof.json。不能称20真实用户、线上采纳率提升或该Skill已达标。
- Playwright真实登录学生账号并在K8s页面完成骑行问答，已出现正文/来源/反馈。发现最近会话混入部门子会话，已加parent_session_id并隐藏内部子会话；跨部门合并来源需偏移编号，子答案未过不能合并标通过，已修复并回归。
- 8条裁判合成校准前后均8/8，不存在67%→100%提升。24题修正提示后原始答案关键点覆盖.97619，裁判21/24，拒答3/3；仍有3条把表格序号当来源编号，保留失败，不称全部原始生成正确。正式Harness有最多两次重写/失败原文退回，后续仍需完整链路验收。
- HPA第1轮基线180并发出现Mongo WaitQueueTimeout(100池/5秒)，1Pod2089请求仅1807成功，保留第一轮报告；扩容观测到13后控制面超时，实际后续16Pod，不能称20通过。
- 第2轮加入32请求背压后，1Pod1677/1677成功；扩容过程中19Pod/15Ready，控制面采样失败，Job实际4654请求3996成功，500/连接/超时均保留。node为本机3CPU/6GB，宿主16GB，不能包装公司级20Pod性能。
- 发现HTTP客户端每次创建TLS上下文、重复题答案缓存会影响容量口径；已加入共享HTTP池与显式缓存开关。第3轮关闭答案缓存、合成模型3秒延时、180并发，暂停仅本次集群的非负载组件以腾资源，保留Mongo/Redis HA+Prometheus/Adapter进行部门组件HPA测试。不是全栈/Qwen吞吐。恢复信息在桌面.local/config/nonload-replicas.json，测试后必须恢复；原本机和knowgo profile未停止。
- 当前第3轮后台进程：/private/tmp/wenshu_run_scale_proof_v3.py，日志wenshu-scale-proof-v3.log，报告hpa-scale-proof.json；前两轮分别hpa-scale-proof-first-failed.json、hpa-scale-proof-v2-partial.json、hpa-scale-v2-job.json。
- 最新已跑131项离线回归通过。新增事实角色/到期与组织引用绑定、反馈去重、SSRF部门ID限制、真正HTTP500观测、并发背压、Prompt/tool_call Skill类型、参数试验管理接口。最新修改仍需最终同步镜像/本机并重跑独立包，不能以早期119项容器结果代替最终。
- 下一步：20Ready和失败率复验→恢复全部暂停组件与port-forward→HA选主/故障注入→日志追踪告警查询→三角色/API上传审核/浏览器→补全矩阵→脱敏无凭证独立交付包/恢复/实测简历。

### 后台异步接续（用户明确授权同一对话继续其他工作）
- 138项最终断网镜像回归通过；随后补全远端部门全部失败时显式回退（先前无提示属于缺陷），新增回归后139项通过，最终镜像仍需重验。
- 真实API三角色、合成上传/自动出题审核/术语审批/有效期/记忆/反馈去重及浏览器三角色已通过。HA Mongo切换与Docker pause Redis主容器20s/Sentinel切换数据保留；Loki符号链接修复后指标/日志/追踪与合成指标告警firing均有证据。
- HPA第三轮最多19Ready，不是20通过。原服务及所有临时暂停部署已恢复，负载mock已删除；失败报告不删除。
- 新增独立配置生成、管理员创建、事实快照导出/空库恢复/active重建脚本。脱敏快照独立库恢复7部门/14版本/67块/5术语，非空恢复拒绝覆盖；未声称向量恢复。
- 最新矩阵逐项关联测试与真实证据，交付包仍pending。继续最终镜像/独立解包/凭证PII扫描/CRC和部署文档，不以本记录宣称全部完成。

### 后台最终验收
- 最终140项回归、断网Python3.11镜像140项与独立解包140项通过。原隐私测试合成编号撞入真实脱敏映射，打包时断言被改写；保留失败，新增原标识消失/匿名替身保留测试，打包器遇到源码私有标识即拒绝静默改写。自动审批原拒绝已凭比对与强化门禁证据解决，没有跳过扫描。
- 真实K8s后勤部门成功加另一部门连接拒绝，以及全部部门失败，均明确partial/降级，不伪装全部验证通过。修复内部部门RPC误走主机代理。
- 最终本机8000/readyz ready、3000 HTTP200；专用K8s业务及观测部署全部Ready，数据库原件保留。最终ZIP独立验收及散列见桌面交付/release.json、reports/package-verification.json。
- 交付内容包括实现、源码、脱敏七样例、49项矩阵、真实报告/失败、独立恢复脚本、简历正文与复盘入口。HPA20稳定容量未达到；不把功能交付等同于该容量指标或用户掌握。
