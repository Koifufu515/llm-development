"""HTTP/Agent检索链路追踪；仅发送到显式配置的本机OTLP Collector。"""
from __future__ import annotations
import functools,os,time,uuid
from contextvars import ContextVar
from prometheus_client import Counter,Histogram

request_id=ContextVar('request_id',default='')
HTTP_REQUESTS=Counter('wenshu_http_requests_total','HTTP请求',['method','route','status'])
HTTP_LATENCY=Histogram('wenshu_http_duration_seconds','HTTP全响应时间',['route'])
_configured=False

def configure(settings):
 global _configured
 if not settings.otel_enabled or _configured:return
 from opentelemetry import trace
 from opentelemetry.sdk.trace import TracerProvider
 from opentelemetry.sdk.resources import Resource
 from opentelemetry.sdk.trace.export import BatchSpanProcessor
 from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
 provider=TracerProvider(resource=Resource.create({'service.name':'wenshu-backend','service.instance.id':os.environ.get('HOSTNAME','native'),'department':settings.dept_id or 'global'}))
 provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_endpoint.rstrip('/')+'/v1/traces',timeout=5)))
 trace.set_tracer_provider(provider);_configured=True

def current_trace_id():
 from opentelemetry import trace
 current=trace.get_current_span().get_span_context()
 return f'{current.trace_id:032x}'if current.is_valid else request_id.get()

def operation_span(name):
 def decorator(fn):
  @functools.wraps(fn)
  async def wrapped(*args,**kwargs):
   from opentelemetry import trace
   with trace.get_tracer('wenshu').start_as_current_span(name)as span:
    model=getattr(args[0],'model',None)if args else None
    if model:span.set_attribute('model',str(model))
    return await fn(*args,**kwargs)
  return wrapped
 return decorator

class TraceMiddleware:
 def __init__(self,app):self.app=app
 async def __call__(self,scope,receive,send):
  if scope['type']!='http':return await self.app(scope,receive,send)
  from opentelemetry import trace,context
  from opentelemetry.propagate import extract
  headers={k.decode():v.decode()for k,v in scope.get('headers',[])}
  parent=context.attach(extract(headers));token=request_id.set(uuid.uuid4().hex)
  started=time.monotonic();status=500
  try:
   with trace.get_tracer('wenshu').start_as_current_span('http.request')as span:
    span.set_attribute('http.request.method',scope['method'])
    async def tracked_send(message):
     nonlocal status
     if message['type']=='http.response.start':
      status=message['status'];message={**message,'headers':[*message.get('headers',[]),(b'x-request-id',current_trace_id().encode())]}
     await send(message)
    try:
     await self.app(scope,receive,tracked_send)
    except BaseException as exc:
     span.record_exception(exc)
     raise
    finally:
     route=getattr(scope.get('route'),'path','unmatched');span.set_attribute('http.route',route);span.set_attribute('http.response.status_code',status)
     HTTP_REQUESTS.labels(scope['method'],route,str(status)).inc();HTTP_LATENCY.labels(route).observe(time.monotonic()-started)
  finally:
   request_id.reset(token);context.detach(parent)
