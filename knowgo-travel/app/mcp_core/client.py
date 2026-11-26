import asyncio
import os
import sys
import shutil

from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import PROJECT_ROOT


async def load_weather_tools():
    # 只传网络代理和模块路径，不把模型凭证传入天气子进程。
    env = {key: value for key, value in os.environ.items() if key.lower() in {"http_proxy", "https_proxy", "all_proxy", "no_proxy"}}
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    client = MultiServerMCPClient({"weather": {
        "transport": "stdio", "command": sys.executable,
        "args": ["-m", "app.mcp_core.servers.amap_weather_server"], "env": env,
    }})
    return await asyncio.wait_for(client.get_tools(), timeout=20)


class ProjectMCPManager:
    """每个服务独立发现与降级，工具调用由适配器创建短会话。"""
    def __init__(self):
        self.tools = {}
        self.status = {}
        self.remote=None

    async def load_service(self, name):
        try:
            if name == 'weather':
                tools = await load_weather_tools()
            elif name == 'search':
                env={k:v for k,v in os.environ.items() if k.lower() in {'http_proxy','https_proxy','all_proxy','no_proxy'}}
                env['PYTHONPATH']=str(PROJECT_ROOT)
                client=MultiServerMCPClient({'search':{'transport':'stdio','command':sys.executable,'args':['-m','app.mcp_core.servers.search_server'],'env':env}})
                tools=await asyncio.wait_for(client.get_tools(),timeout=20)
            elif name == 'rail':
                command = shutil.which('node')
                if not command:
                    raise RuntimeError('Node runtime not found')
                client = MultiServerMCPClient({'rail': {
                    'transport':'stdio', 'command':command,
                    'args':[str(PROJECT_ROOT/'infra/rail-mcp/node_modules/12306-mcp/build/index.js')],
                }})
                tools = await asyncio.wait_for(client.get_tools(), timeout=20)
            elif name in ('amap','flight','hotel','bailian_search'):
                if self.remote is None:raise RuntimeError('Remote providers not attached')
                tools=await self.remote.discover('search' if name=='bailian_search' else name)
                if not tools:raise RuntimeError('未取得查询工具')
            elif name in ('backup_weather','image_search'):
                from app.config import Settings
                settings=Settings();url=settings.backup_weather_mcp_url if name=='backup_weather' else settings.image_search_mcp_url
                if url:cfg={'transport':'streamable_http','url':url}
                else:
                    module='app.mcp_core.servers.weather_server' if name=='backup_weather' else 'app.mcp_core.servers.image_server'
                    env={k:v for k,v in os.environ.items() if k.lower() in {'http_proxy','https_proxy','all_proxy','no_proxy'}};env['PYTHONPATH']=str(PROJECT_ROOT)
                    cfg={'transport':'stdio','command':sys.executable,'args':['-m',module],'env':env}
                tools=await asyncio.wait_for(MultiServerMCPClient({name:cfg}).get_tools(),20)
            else:raise ValueError('未知MCP服务')
            self.tools[name] = tools
            self.status[name] = 'ready'
        except Exception:
            self.tools[name] = []
            self.status[name] = 'unavailable'
        return self.tools[name]

    async def initialize(self):
        await asyncio.gather(self.load_service('weather'), self.load_service('rail'), self.load_service('search'))

    async def attach_remote(self,remote):
        """终版0672的另外四类HTTP MCP；两个仅在说明中出现的扩展地址可选。"""
        self.remote=remote
        await asyncio.gather(*(self.load_service(name) for name in ('amap','flight','hotel','bailian_search','backup_weather','image_search')))

    async def rebuild_service(self,name):
        self.tools.pop(name,None)
        if self.remote and name in ('amap','flight','hotel','bailian_search'):
            service='search' if name=='bailian_search' else name
            self.remote.tools.pop(service,None);self.remote.fingerprints.pop(service,None)
        return await self.load_service(name)

    def registered_tools(self):
        """同一注册表给模型和ToolNode；跨服务重名保留为service__tool，不覆盖主服务。"""
        output={}
        for service,tools in self.tools.items():
            for tool in tools:
                name=tool.name
                # 仅注册查询类工具，项目不执行酒店预订、支付或取消订单。
                if any(w in name.lower() for w in ('book','reserv','payment','purchase','cancel','order','create','update','delete','refund','pay')):continue
                if name in output:
                    name=service+'__'+name;tool=tool.model_copy(update={'name':name})
                from app.full.rail_guard import _guard_train_tool
                output[name]=_guard_train_tool(tool)
        return output
