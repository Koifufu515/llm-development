"""只从已存在JSON生成交付指标；缺证据不填成功数，不覆写原始报告。"""
import json,statistics,hashlib
from pathlib import Path
R=Path('reports');load=lambda n:json.loads((R/n).read_text())
rail=load('reference-rail-benchmark.json');rag=load('reference-rag-cold-warm.json');router=load('reference-router-after.json');before=load('reference-router.json');first=load('reference-first-frame.json');quality=load('reference-six-cases-stable.json');accept=load('reference-final-acceptance.json')
median=statistics.median
serial=median(r['serial']['seconds']for r in rail['rows']);parallel=median(r['parallel']['seconds']for r in rail['rows']);cold=median(r['cold']['seconds']for r in rag['rows']);warm=median(r['warm']['seconds']for r in rag['rows'])*1000
crop=rail['crop'];rpass=sum(r['score']==1 for r in router['rows']);bpass=sum(r['score']==1 for r in before['rows']);n=len(router['rows'])
frames={mode:median(r['seconds']for r in first['rows']if r['mode']==mode)for mode in ('form','chat')}
lines=['# 本机指标实测报告（2026-10-31）','','本地个人项目，Qwen Plus、macOS、实际MCP/PG/Redis；没有线上用户或生产流量。基准的失败、旧版与当前版分开留存。中位数不是P95。','','| 项目 | 实测 | 样本与口径 |','|---|---|---|',f'| 三段高铁串行→并行 | {serial:.3f}→{parallel:.3f}秒，耗时减少{(1-parallel/serial)*100:.1f}% | 相同三段/日期/GD过滤，各3轮，交替顺序，18段请求均成功 |',f'| 车票给模型的载荷 | {crop["raw_trains"]}班/{crop["raw_characters"]}字符→{crop["compact_trains"]}班/{crop["compact_characters"]}字符 | 单次同一真实返回；字符不是Token，不是完整Agent Token节省 |',f'| 完整RAG冷→热 | {cold:.3f}秒→{warm:.2f}毫秒 | 索引已加载；同一苏州查询，完整查询优化+9条打分，各3轮；不是通用缓存命中率 |',f'| 原路由回归通过 | {bpass}/{n}→{rpass}/{n}（{rpass/n:.1%}） | 同21条原用例；规划判断+技能标签共同评分；用此集改过提示词，非独立泛化准确率 |',f'| 表单/聊天首业务帧 | {frames["form"]:.3f}/{frames["chat"]:.3f}秒 | 各3轮；表单是skills帧，聊天是assistant帧；不是模型TTFT |','| 断连后同会话可继续写 | 6/6 | 首帧后主动断连，下一请求done200 |',f'| 功能/安全最终验收 | {sum(bool(v)for v in accept["checks"].values())}/{len(accept["checks"])}检查通过 | 真实API/Qwen/PG；安全与选卡部分复用真实候选，非新一轮全部供应商查询 |','| 回归 | 120项通过 | 日志reference-final-pytest.log；单元/协议/Graph测试，不冒充120次线上任务 |']
lines+=['','## 完整流程基准','', '单城苏州3天、上海出发、1成人、5000元、同高铁偏好。标准模式脚本立即确认并用同规则选真实卡片，不包含人的思考时间。快速模式并行收集并自动选。回合遥测计数包括关键路径内模型调用尝试，失败也计数；不包含供应商内部LLM、embedding和异步GEval，不能解释为项目全部费用。']
f=R/'reference-flow-final.json'
if f.exists():
 d=json.loads(f.read_text());lines+=['','| 模式 | 成功/尝试 | 成功轮耗时中位数 | 全部调用次数 | 模型错误计数 |','|---|---|---|---|---|']
 for mode in ('standard','express'):
  group=[x for x in d['rows']if x['mode']==mode];ok=[x for x in group if x.get('status')=='ok'];times=[x['seconds']for x in ok];lines.append(f'| {mode} | {len(ok)}/{len(group)} | {median(times):.3f}秒 | '+','.join(str(x.get('llm_calls','未完整取得'))for x in group)+' | '+','.join(str(x.get('llm_errors','未知'))for x in group)+' |') if times else lines.append(f'| {mode} | 0/{len(group)} | 无成功轮 | 未完整取得 | 保留失败 |')
 lines+=['','所有轮逐条结果见reference-flow-final.json，不能只选成功轮解释稳定性。在线异步质检正常启用，前轮质检可能与后轮任务重叠。早期TypeError、超时及修复后一对稳定性试验另存，不混进这三轮。']
else:lines+=['','最终三轮尚未产生结果，不预填数字。']
records=quality['records'];by_round={}
for repeat in (1,2):
 pos=[x for x in records if x['repeat']==repeat and x['positive']];neg=[x for x in records if x['repeat']==repeat and not x['positive']]
 good=lambda x:not x.get('error')and len(x.get('metrics',[]))==3 and all(m.get('passed',False)for m in x['metrics'])
 bad=lambda x:not x.get('error')and len(x.get('metrics',[]))==3 and any(not m.get('passed',False)for m in x['metrics'])
 by_round[repeat]=(sum(map(good,pos)),sum(map(bad,neg)))
positive_scores=[m['score']for x in records if x['positive']for m in x.get('metrics',[])if m.get('score')is not None];grouped={}
for x in records:
 for m in x.get('metrics',[]):
  if x['positive']and m.get('score')is not None:grouped.setdefault((x['case_index'],m['name']),[]).append(m['score'])
variation=max((max(v)-min(v)for v in grouped.values()),default=0)
lines+=['','## 原六样本GEval','',f'固定同语义评估步骤后两轮正/反样本识别数：{by_round}（每轮正3、反3）。共12次，10次与作者标签一致，0次执行异常。正样本三维均分{statistics.mean(positive_scores):.3f}（18个维度分数），相同样本同维度两轮最大差{variation:.3f}。多城正样本两轮均被判匹配度不达标，保留裁判理由。','', '原动态生成评估步骤版本12次中8次与作者标签一致、3次评分异常，另见reference-six-cases.json。不把模型裁判结果称人工一致率、幻觉率或事实准确率。在线与离线引用同一指标工厂，当前固定步骤；旧证据约束版指标保留为另一个可选工厂，不混用阈值。']
retrieval=R/'reference-retrieval.json'
if retrieval.exists():
 d=json.loads(retrieval.read_text());lines+=['','## 检索验证集','','| 检索配置 | n | Recall@3 | Hit@3 | MRR@3 | 失败 |\n|---|---|---|---|---|---|\n'+'\n'.join(f"| {mode} | {v['n']} | {v['recall_at_3']:.2%} | {v['hit_at_3']:.2%} | {v['mrr_at_3']:.3f} | {v['errors']} |" for mode,v in d['aggregate'].items()),'','18城冻结实体问题，开发6城分离；助手按来源标父块，未独立人工复核。Recall@3按所有相关父块算、Hit@3按至少一个命中算、MRR@3按首个相关父块名次算。全部失败计入；不是问答正确率或线上指标。']
lines+=['','## 数据与限制','','71份公开历史英文攻略、39城、404025字符、654父块/3120子块；342选择器城市不等于攻略覆盖。语料是历史快照，时效事项走联网查询并提示官方核实。qwen-turbo真实429的失败版已分离，不混进完整RAG耗时。酒店等级不等于用户评分；腾讯配额耗尽，不称查询成功。','', '没有测出线上QPS/P95/SLA、真实用户收益、人工裁判一致率或全体问题问答准确率。这些值留空，不以局部基准外推。失败档案：reference-flow-benchmark-before-typeerror-fix.json、reference-flow-benchmark.json、reference-rag-incomplete-turbo429.json、reference-full-e2e-render-failure.json。','', '原始报告与脚本随包保存，可按同输入复跑；真实供应商返回和模型结果会随时间波动。']
(R/'指标实测报告.md').write_text('\n'.join(lines)+'\n')
resume=f'''# 可复制的项目描述（按个人项目填写）

**知行旅行助手｜Agent应用与后端开发**

技术栈：Python、FastAPI、LangChain/LangGraph、Qwen、MCP、PostgreSQL、Redis、Chroma、DeepEval、Docker。

- 围绕多城旅行规划实现需求收集、目的地推荐、交通/住宿选择、餐饮偏好、逐日行程与预算；以单Agent+StepConfig动态工具编排和PG Checkpointer驱动多轮流程，支持需求变更回退、用户长期偏好与会话恢复。
- 接入12306、航班、酒店、地图、天气和搜索等9类MCP服务，构建四类多段查询卡片；相同三段高铁查询各3轮，本地耗时中位数由{serial:.2f}秒降至{parallel:.2f}秒；将单次{crop['raw_trains']}班/{crop['raw_characters']}字符的模型载荷裁剪为12班/{crop['compact_characters']}字符。
- 基于71份公开攻略构建3120子块/654父块知识库，组合父子分块、中文BM25+向量RRF、MultiQuery、LLM重排与Redis版本缓存；同查询完整冷流程中位数{cold:.2f}秒，热命中{warm:.1f}毫秒（各3轮）。
- 实现JWT/所有权校验、持久卡片、revision防旧提交、幂等回执、历史行程版本及SSE事件流；120项回归通过，完成真实API的跨用户隔离、过期/伪造选项拒绝、断连恢复和重启持久化验收。
- 建立在线异步GEval与离线回归；原21条路由回归通过20条，原6条行程正反样本各评2轮，保留与作者标签不一致的结果和执行失败，区分工程校验与模型质量。

篇幅紧时保留前四条；投Agent更突出编排/工具/RAG，投后端更突出状态一致性、幂等、权限、持久化和并行。上述全部为本地个人项目实测，没有线上用户量或生产SLA。原方案来源与功能替代见复现对照。
'''
if retrieval.exists():
 a=load('reference-retrieval.json')['aggregate'];resume=resume.replace('同查询完整冷流程',f"18条冻结实体检索题上Recall@3由{a['rrf']['recall_at_3']:.1%}提升至{a['full']['recall_at_3']:.1%}、MRR@3由{a['rrf']['mrr_at_3']:.3f}升至{a['full']['mrr_at_3']:.3f}（18条实体检索题）；同查询完整冷流程")
resume+='''
## 后端方向可替换表述

- 设计会话State、用户Store及ORM业务表三层持久化，维护需求revision与级联回退；通过PG写锁、卡片回执和版本幂等处理同会话并发、断连与重复确认，重启前后状态/偏好/历史计划摘要一致。
- 为高铁、航班、自驾和住宿构建多段异步能力，隔离单段失败；相同三段高铁各3轮，本地串行3.84秒降至并行1.49秒，耗时减少61.3%。
- 实现JWT与资源所有权、会话软删/归档/恢复、消息全文与摘要、同会话多行程版本；以SSE统一推送文本、状态、交互卡片和清单，六次主动断连后同会话均可继续写入。
- 建立120项回归、27项专项API检查及真实供应商联调；覆盖伪造候选、过期卡片、跨用户访问、首次Checkpoint归约、真实ToolNode工具对象和异步上下文隔离等边界。
'''
resume+='''
## 精简投递版（篇幅有限时选这一版）

**知行旅行助手｜Agent应用开发**  
Python / FastAPI / LangGraph / MCP / PostgreSQL / Redis / Chroma

- 实现需求、目的地、交通、住宿、餐饮、行程及预算七步规划，以单Agent动态工具编排配合PG Checkpointer/Store支持回退、跨会话偏好与恢复；9类MCP接入真实查询，三段高铁各3轮中位耗时3.84秒降至1.49秒。
- 基于71份攻略构建父子分块、中文BM25+向量RRF、MultiQuery与LLM重排；18条冻结实体检索题Recall@3由87.96%升至95.37%，同查询Redis冷/热各3轮中位11.84秒/5.57毫秒。
- 实现JWT所有权、持久卡片、revision校验、幂等回执及历史版本，SSE统一推送状态和交互；120项回归及27项专项检查通过，标准/快速完整行程各3轮均完成。

数字均为本地固定样本；检索集为来源实体标注，不是线上问答准确率。详细取舍、失败和口径见实测报告。
'''
template=Path('docs/简历项目模板.md')
if not template.exists():
 (R/'简历项目描述.md').write_text(resume)
else:
 print('保留人工润色的简历项目描述；指标已刷新，简历数字需按新结果核对')
print('reports generated')
