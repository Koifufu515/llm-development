import asyncio
import pytest
from app.utils.concurrency import bounded_execution

@pytest.mark.asyncio
async def test_harness_backpressure_and_cancel_do_not_leak_slots():
 class Service:
  def __init__(self):self._request_slots=asyncio.Semaphore(2);self.running=0;self.peak=0
  @bounded_execution
  async def answer(self):
   self.running+=1;self.peak=max(self.peak,self.running)
   try:await asyncio.sleep(.02);return {}
   finally:self.running-=1
 service=Service();tasks=[asyncio.create_task(service.answer())for _ in range(12)]
 await asyncio.sleep(.001);tasks[-1].cancel()
 results=await asyncio.gather(*tasks,return_exceptions=True)
 assert service.peak==2 and service._request_slots._value==2
 assert any(isinstance(r,asyncio.CancelledError)for r in results)
 assert max(r['queue_wait_ms']for r in results if isinstance(r,dict))>20
