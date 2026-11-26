"""生成隔离Compose配置；不读取其他项目凭证、不覆盖已有配置。"""
from pathlib import Path
import secrets
r=Path(__file__).resolve().parents[1];p=r/'.local/config/compose.env';p.parent.mkdir(parents=True,exist_ok=True)
if p.exists():raise SystemExit('已有配置，未覆盖：'+str(p))
mongo,redis,auth,internal=[secrets.token_hex(24)for _ in range(4)]
values={'FULL_MONGO_PASSWORD':mongo,'FULL_REDIS_PASSWORD':redis,'FULL_MONGODB_URI':f'mongodb://wenshu:{mongo}@mongodb:27017/wenshu_full?authSource=admin','FULL_REDIS_ADDR':f'redis://:{redis}@redis:6379','AUTH_SECRET':auth,'INTERNAL_API_TOKEN':internal,'DEEPSEEK_BASE_URL':'https://dashscope.aliyuncs.com/compatible-mode/v1','DEEPSEEK_MODEL':'qwen-plus','DEEPSEEK_API_KEY':'','RELAY_BASE_URL':'https://dashscope.aliyuncs.com/compatible-mode/v1','RELAY_API_KEY':'','EMBEDDING_PROVIDER':'relay','EMBEDDING_MODEL':'text-embedding-v4','EMBEDDING_DIM':'1024','RERANKER_ENABLED':'true','RERANKER_MODEL':'qwen3-rerank','RERANKER_URL':'https://dashscope.aliyuncs.com/compatible-api/v1/reranks','MODEL_EGRESS_ALLOWED':'false','PI_AGENT_ENABLED':'true','SEED_DEMO_USERS':'false'}
p.write_text(''.join(f'{k}={v}\n'for k,v in values.items()));p.chmod(0o600)
private=r/'.local/private';private.mkdir(parents=True,exist_ok=True);mapping=private/'privacy-map.json'
if not mapping.exists():mapping.write_text('{}');mapping.chmod(0o600)
print('已生成本机私有配置。填入百炼Key、配置脱敏映射并确认授权后，将MODEL_EGRESS_ALLOWED改true；未输出凭证。')
