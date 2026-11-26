from types import SimpleNamespace
import pytest
from app.full.memory import UserMemoryService
class Store:
 def __init__(self):self.data={}
 async def aget(self,namespace,key):
  value=self.data.get((namespace,key));return SimpleNamespace(value=value) if value is not None else None
 async def aput(self,namespace,key,value):self.data[(namespace,key)]=value

@pytest.mark.asyncio
async def test_original_typed_history_and_accommodation_budget():
 s=Store();m=UserMemoryService(s)
 await m.update_dietary_restrictions('u',['海鲜过敏','海鲜过敏'])
 await m.update_accommodation_preference('u',['经济酒店'],400)
 await m.update_accommodation_preference('u',['民宿'],600)
 await m.add_completed_trip('u','苏州','2026-10-01','2026-10-03',['拙政园','拙政园'])
 memory=await m.get_user_memory('u')
 assert memory.profile.dietary_restrictions==['海鲜过敏']
 assert memory.history.accommodation_preference.avg_budget_per_night==500
 assert memory.history.visited_attractions==['拙政园']
 assert memory.history.completed_trips[0].end_date=='2026-10-03'
 assert not (await m.get_user_memory('other')).history.completed_trips
 assert '500' in await m.format_memory_for_prompt('u')
