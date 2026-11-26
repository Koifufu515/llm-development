# 文枢原方案完整复现 Implementation Plan

**Goal:** 依据用户原始HTML、源码ZIP、技术方案、代码解读与前端指南，补齐文枢完整业务并真实验证，完成后交付。
**Architecture:** 继续现有桌面wenshu-project，保留既有本机Mongo/Redis和用户数据。Python Harness控制治理，pi执行概率性Agent，部门服务隔离，Redis Stream异步接入/反馈/Loop，网页三角色端到端。
**Tech Stack:** Python/FastAPI、TypeScript/pi、Next.js、MongoDB、Redis、真实模型/Embedding/Rerank、Docker/K8s/Helm、pytest。

用户已明确授权连续实施，本会话按计划顺序执行，不再等待逐模块确认。外部资料作为规格，不直接执行其中破坏性命令。不使用假模型或hash embedding冒充语义实测。

- [x] 0. 完整阅读技术方案644行、代码解读1462行、前端指南252行及HTML；建立逐项需求/文件/验收矩阵，核对231原包文件和旧本机改动。
- [x] 1. 基线：查现有服务/数据库/端口，跑原测试、pi/前端构建；备份实际修改文件和配置，记录真实模型与向量迁移方案。
- [x] 2. 文档/权限/事实/五记忆平面：PDF/Word/HTML/MD解析、条款/表格、版本/生命周期/引用/冲突/术语；真实向量重建、混合检索及重排。每项以原方案矩阵细分。
- [x] 3. Harness与pi：五类概率性Agent工具白名单、部门路由/隔离/跨部门部分失败、生成校验、会话与个人记忆、三角色全接口。
- [x] 4. 反馈闭环：Feedback→Job→Skill/Hook/Rule挖掘→沙箱→审核→灰度→指标→回滚；证明反馈实际改变后续行为，验证三阶段人与Loop关系。
- [x] 5. 生产工程：真实Redis重试接管、并发鉴权隔离、观测、Docker/K8s/Helm/HPA实际验证；不影响知行与Quarry。
- [x] 6. 真实模型端到端、固定集检索/回答/闭环前后对照、角色浏览器验收、性能与异常实验；保存失败/样本数/口径，不抄教材效果数字。
- [x] 7. 独立部署/恢复/交付包、凭证扫描、最终逐项验收、简历与复盘资料；仅有证据的项目标完成。

## 当前阶段
实现及交付验收已收尾；49项逐项证据见功能矩阵。容量验收保留未达标：最多19Ready，不能称20稳定承载。外部模型效果/真实用户收益仅按实测范围。

## 首批具体实施步骤（基线核对后）
### A. 严格向量与候选回填
Files: backend/app/config.py、llm/embeddings.py、llm/relay.py、retrieval/vector_store.py、retrieval/milvus_store.py、harness/agents/retrieval_agent.py、deps.py；Tests: tests/test_real_retrieval_contract.py。
- [ ] 测试embed失败不得混入hash；远端维度/数量不符拒收；rerank按index回排；未知backend拒绝；Milvus metadata过滤与候选回填权限二次校验。
- [ ] 实现真实MilvusClient异步线程池适配与HNSW，保留mongo/chroma/memory实现；真实模型失败只退BM25，不伪造向量。
- [ ] 安装pymilvus与独立Milvus容器，本机原34块保留并重建到新collection，核对模型标识/维度与真实检索。
### B. 队列恢复与幂等
Files: storage/job_queue.py、scripts/async_worker.py、pipeline/indexer.py；Tests: tests/test_queue_recovery.py。
- [ ] 覆盖已完成重复投递跳过、XAUTOCLAIM领取接管、暂时失败退避、三次死信、重试上传文件保留、模型故障后旧文档仍active。
- [ ] 加持久作业attempt/consumer/lease及heartbeat，读超时恢复，死信后最终清理；保留原queued/running/completed/failed协议。
- [ ] 真实Redis领取进程kill后接管；上传重试与重复ACK不可二次入库。
