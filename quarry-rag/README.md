# Quarry — 面向 Agent 的 RAG 检索平台

按用户提供的《Quarry - RAG 检索平台》和《代码文档》八章复现。原始512代码块、文件映射及修复记录均保留在docs/。它作为独立项目返回证据、引用、事实状态与拒答建议；上游知行等Agent通过单文件SDK消费证据并生成回答。

## 最终验收（2026-11-09）

49项回归与独立解包49项通过，最终镜像与真实API/SDK/上传复验完成。范围见[逐项验收](docs/原文逐项验收.md)，证据见[最终验收](reports/最终交付验收.md)，投递文案见[简历正文](reports/简历项目描述.md)。实测失败与口径限制保留在[实测报告](reports/实测报告.md)。

## 当前入口

- 开发检索调试台：http://127.0.0.1:8110/web/debug.html
- 生产API与健康探针：http://127.0.0.1:8113/healthz
- 接口文档：http://127.0.0.1:8113/docs
- RedisInsight：http://127.0.0.1:8101
- 最终评测报告：eval/report-release.html；实测数据：reports/delivery-measurements.json。

原8100已有其他程序，8001为知行，本项目使用独立端口。PostgreSQL5433、Redis6380。基础设施仍是原方案的PostgreSQL17+pgvector0.8.6与Redis Stack两个容器；生产API、开发API和worker是应用进程的容器化部署。未替换知行现有RAG默认实现。

## 已实现的业务链

1. Markdown/txt和Word解析；结构化标题、父子块、表格/代码原子片段、原文区间及跨进程稳定ID。
2. 文件SHA与块ID两级幂等、选择性向量化、文档版本退役、孤儿清理、ACL同步刷新、撤回与集合蓝绿事务切换。
3. Redis Stream消费者组、PEL接管、三次失败死信、鉴权上传与状态查询；API与worker共享持久化语料卷。
4. halfvec1024/HNSW与jieba+PG全文双路召回，在一条SQL里过滤并RRF融合；迭代扫描、薄Retriever/Fake契约、线程池、三列调试台和EXPLAIN实验。
5. 百炼qwen3-rerank/Noop及失败回退，同节去重、父块/邻块回捞、三档上下文预算、来源与字符/段落级引用、dense阈值拒答建议。
6. 离线事实抽取、严格quote校验、抽取缓存、官方CSV事务替换、别名/季节匹配、verified/expired/unverified、占位符遮蔽和来源核实日期。
7. 固定标注集、金块区间命中、MRR/拒答/裁判支撑率、开关对照、分阶段压测、回归闸门与独立HTML报告。
8. Key哈希、服务端权限与集合白名单、租户绑定、Redis额度、结构化错误、总超时、请求ID日志、查询分析SQL、重试SDK、Docker与迁移。

逐项来源和证据见docs/原文逐项验收.md；修复均保留红/绿结果，不能仅用通过测试数代替范围验收。

## 启动与配置

当前机器已配置，无需重新填写。新环境复制.env.example为.env，在本机填写PostgreSQL密码与百炼Key。使用uv和Docker：

```bash
bash scripts/bootstrap.sh
```

Mac当前机器可显式指定已安装的工具与现有代理：

```bash
QUARRY_UV=/Users/jarvis/Desktop/大模型开发/.tools/uv/bin/uv \
QUARRY_DOCKER_CONTEXT=colima-knowgo \
QUARRY_HTTP_PROXY=http://192.168.5.2:7897 bash scripts/bootstrap.sh
```

启动脚本按原顺序执行依赖安装、初始化SQL、单独迁移、幂等接入、离线事实抽取及服务启动。使用命名卷是为了兼容当前Colima挂载范围，不重启承载知行的虚拟机。不执行down -v，不自动删除已有业务数据。

运行中的语料以Docker共享corpusdata卷为准，仓库corpus目录是种子和本机实验副本。所有服务端接入/校验命令可在worker中运行，避免混用两个文件视图：

```bash
docker --context colima-knowgo compose -p quarry-rag exec worker uv run --no-sync python -m quarry.scripts.verify_citations
```

需改动文档时通过上传接口提交新版本，或在同一个corpus卷中修改后运行接入脚本；不要只改宿主机副本而误以为容器已同步。

## Key与SDK

当前检索Key保存在本机private/knowgo-key.txt，接入Key在private/ingest-key.txt，均为600权限，不进入版本库或交付包。检索Key不能上传，上传需要服务端role:ingest标签。新环境分别签发：

```bash
uv run --no-sync python -m quarry.scripts.create_api_key --caller knowgo-travel --tenant demo --collections travel-guide --labels public --rate-limit 120
uv run --no-sync python -m quarry.scripts.create_api_key --caller quarry-ingest --tenant demo --collections travel-guide corp-policy internal-notes --labels public org:demo-corp role:ingest
```

在本机设置QUARRY_URL=http://127.0.0.1:8113和QUARRY_KEY后，运行：

```bash
uv run --no-sync python sdk/example.py "南普陀寺开放时间"
```

上游复制sdk/quarry_client.py即可。生成模型读取context与facts，text保留原文用于高亮。Key的标签和租户由服务端确定，请求体不能越权指定。

## 验证与恢复

```bash
uv run --no-sync pytest tests/unit tests/contract tests/redlines -q
uv run --no-sync python scripts/verify_workflows.py
uv run --no-sync python scripts/verify_queue_recovery.py
uv run --no-sync python scripts/verify_tenant_api.py
uv run --no-sync python -m quarry.scripts.compare_eval --base release-baseline --new release-full --gate
```

全量红线需真实PG/Redis、已接入语料和可用模型Key；纯契约测试另见.github/workflows/checks.yml，不用Fake结果冒充语义检索效果。快照导出不含向量，恢复脚本校验SHA、沿用chunk_id并真实重算子向量，默认只创建building集合，不替换active：

```bash
uv run --no-sync python -m quarry.scripts.export_snapshot travel-guide
uv run --no-sync python scripts/restore_snapshot.py snapshots/travel-guide --tenant snapshot-recovery
```

## 数据和结果的含义

公共语料来自中文维基导游，保留来源、许可证和抓取时间；企业制度、内部笔记、Hello及上传验收文档均为演示数据。抓取日期不代表票价/开放时间最新。原文三行官方CSV也是演示，保留在official/demo-travel-guide.csv，没有伪装成真实核验；当前维护表包含从秦始皇帝陵博物院官网核对的3条季节键常规票价（同一政策），其余提及保持unverified；来源及核实范围见official/核实记录.md。事实过期、冲突与更新另在隔离集合真实验收。

40题由模型起草、助手对照源块筛选，不是独立人工评测。命中率的分母是32条有答案查询，指标指至少一块金块进Top5；裁判评证据是否足够，不评现实事实准确率。实时余票等近领域无答案仍有误放行，见实测报告。各轮延迟和失败全部保留，800ms是原目标，不是承诺稳定达到的线上SLA。

原文明确只讲不做的ES/分区、PDF/Excel/OCR、本地ONNX及查询改写仍按原边界保留方案说明，未冒称实现。向量列固定1024维，不能改模型后直接复用旧索引；迁移模型/维度需按原文重建、核对配置后切换。原始代码文档提供的是章节代码，当前为逐文件重建，不冒称取得原作者仓库或线上生产系统。

复盘从docs/复盘入口.md沿一条完整请求讲起；助手实现、助手验证与用户掌握分别记录。
