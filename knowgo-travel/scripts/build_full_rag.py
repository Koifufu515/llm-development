"""从已保存、有来源的攻略JSON幂等构建正式检索索引。"""
import asyncio,json
from app.full.knowledge import AdvancedKnowledge
async def main():
    knowledge=AdvancedKnowledge()
    try:print(json.dumps(await knowledge.load(build=True),ensure_ascii=False,indent=2))
    finally:await knowledge.close()
if __name__=='__main__':asyncio.run(main())
