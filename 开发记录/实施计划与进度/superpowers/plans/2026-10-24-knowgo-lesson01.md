# 知行旅行助手第一步 Implementation Plan

> Execute inline with the user, one lesson at a time. 本轮只实现服务骨架，不跳到后续 Agent、数据库或 MCP 模块。

**Goal:** 建立独立 Python 3.13 环境，运行一个有根接口和自动文档的 FastAPI 服务，并让用户看懂最小代码。

**Architecture:** 用户后续指定与文枢放在一起，实际项目目录改为 `/Users/jarvis/Desktop/大模型开发/knowgo-travel`，独立工具在同级 `.tools`。`app/main.py` 是入口；服务监听本机 8001 端口。数据库与模型业务接入不属于本课。

**Tech Stack:** Python 3.13、uv、FastAPI 0.124.4、Uvicorn。

## Task 1: 环境

- [x] 检查现有 Python、uv、Docker 和端口。已检测到 Python 3.10，uv/Docker 不在 PATH。
- [x] 使用 PyPI 官方 uv 包安装 uv 0.13.5；用户要求后已将可用工具复制到桌面同级 `.tools/uv`。
- [x] 安装 Python 3.13.17，桌面项目创建独立 .venv，依赖已下载并锁定。

## Task 2: 最小服务

**Files:**
- Create: `knowgo-travel/pyproject.toml`
- Create: `knowgo-travel/.python-version`
- Create: `knowgo-travel/.gitignore`
- Create: `knowgo-travel/app/__init__.py`
- Create: `knowgo-travel/app/main.py`
- Create: `knowgo-travel/scripts/dev.sh`
- Create: `knowgo-travel/README.md`
- Create: `knowgo-travel/学习记录.md`

- [x] 创建依赖声明：Python `>=3.13,<3.14`；`fastapi==0.124.4`；`uvicorn[standard]>=0.35,<1`；`[tool.uv] package=false`。
- [x] 应用代码：

```python
from fastapi import FastAPI

app = FastAPI(title="知行旅行助手", version="0.1.0")


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "message": "知行旅行助手后端已启动"}
```

- [x] `scripts/dev.sh` 使用 `set -eu`，解析自身所在的项目目录，设置同级工具路径，然后执行：

```bash
exec "$workspace_dir/.tools/uv/bin/uv" run --frozen uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

- [x] 执行 uv sync，生成 uv.lock 与项目虚拟环境。

## Task 3: 验证与第一课

- [x] 在桌面项目目录启动 `./scripts/dev.sh`，执行会话 99044，reloader PID 79954/server PID 79957（后续可能变化）。
- [x] 使用标准库 urllib 验证 GET `/`、`/docs`、`/openapi.json` 为 HTTP 200；根 JSON status=ok；OpenAPI 含根 GET；GET `/missing` 为 HTTP 404。
- [x] uv lock --check 通过；独立 Python 版本 3.13.17。
- [x] 记录 app 对象、路由装饰器、async 函数、JSON 返回和 Uvicorn 之间的职责。
- [ ] 用户练习：修改 message 并刷新接口，观察 reload 生效。用户完成练习前不标记“已掌握”。

这类最小、低影响骨架使用 HTTP 冒烟验证，不另写只镜像实现的单元测试。不自动提交 Git。

## 用户追加：安装和配置 Docker

- [x] 用户明确授权自动下载配置 uv/Docker，并要求项目放到桌面「大模型开发」。
- [x] 检查 macOS 26.5.1 arm64；未找到现成 Docker.app 或 Docker CLI。
- [x] Docker Desktop 官方下载连续两次连接被重置（含 HTTP/1.1 诊断），系统无已配置代理；没有关闭 TLS 校验或接受许可协议。
- [x] 使用 Homebrew 官方 formula 安装 uv 0.13.5、colima 0.10.3、docker 29.9.2、docker-compose 5.6.1（依赖 lima 2.2.1）；禁用自动更新/清理。官方源较慢，确认清华同包可用后用 HOMEBREW_BOTTLE_DOMAIN 临时镜像安装，Homebrew 校验哈希。
- [x] 启动独立 Colima 配置，验证 Docker daemon/Compose，运行官方 hello-world，退出码 0。
- [x] 将真实环境结果、后续启停命令更新到桌面项目 README 和学习记录。

## 排查记录

- curl 下载 desktop.docker.com 返回连接重置，不归因为项目代码问题。
- 默认受限沙箱不能连接 localhost，首次 HTTP 检查返回 PermissionError；使用已授权的沙箱升级后 HTTP 验证通过。
- brew 提示另一个现存第三方 tap 不受信任；不修改其信任设置，只使用官方公式安装所需工具。
- Compose 插件已注册到 ~/.docker/cli-plugins/docker-compose，docker compose version=5.6.1。
- 已创建桌面知行项目四个 .command 入口：启动后端、启动容器环境、停止容器环境、查看环境。
- Colima 启动会话 77574：profile=knowgo，2核/3GB/20GB，vz，Docker runtime，仅挂载桌面知行目录。仍在下载首次虚拟机镜像。
- 官方镜像：colima-core v0.10.4，ubuntu-24.04-minimal-cloudimg-arm64-docker.raw.gz，332354401字节。GitHub asset API ID=437242106。
- 官方 SHA-256=1fc0354f4f99734ce3886628cc7af8b0437c1a1d391b126bd09cba0df35ee53f；官方清单 SHA-512=32242674b046b5057e60c4aba334b51e3665f05412cda89ed081cc2de153ae5c41f6b105b5c442cbe48d78e2cc21e9ba1950e406b6fb4fc2fd1dd2259240abbd。
- colima 下载缓存键=b0992ab88f5a3c0c436bbb3065c01466f20dc1dd0eb0a60299d410176f21a1c3；原始缓存目录=~/Library/Caches/colima/caches。
- 直接 GitHub 镜像慢，已通过官方 API octet-stream 下载到 /private/tmp/knowgo-colima-arm64-docker.raw.gz，下载会话 78131。完成后先校验，再停止原下载，将完整文件放入对应 Colima 缓存键，并重启 knowgo 配置。Docker daemon 与容器尚未验证。
- 单流下载速度不足，已依次停止 78131、镜像加速尝试 28860、原 Colima 下载 77574。未改变现有 VM 数据盘。
- 已验证官方 release-assets 直连支持 Range（64KB试验，返回65536字节）；当前用64个约5MiB分段并行下载，执行会话70769，脚本 /private/tmp/knowgo_download_colima_parts.py。合并输出 /private/tmp/knowgo-colima-arm64-docker-complete.raw.gz，脚本会强制校验上述 SHA-256/SHA-512。
- 官方签名直连URL暂存 /private/tmp/knowgo-colima-asset-direct-url.txt，不在日志/用户文档中打印。分段目录 /private/tmp/knowgo-colima-parts。
- 完成后将校验通过的完整文件复制到 Colima cache 的 b099...c3（无.downloading后缀），再次 colima start knowgo，然后 docker --context colima-knowgo info 和 hello-world 验证。
- 大分段在300秒附近有少数超时重试，已停止70769，保留已完成部分。当前用512KiB小段补齐剩余32MiB，脚本 /private/tmp/knowgo_resume_colima_parts.py，下载会话73487；仍输出同一个 complete.raw.gz 并强制双重哈希校验。
- 73487 已成功：剩余64小段24.2秒完成，官方 SHA-256/SHA-512 均通过。完整镜像已复制到对应 Colima 缓存。
- 会话97249启动成功，Docker context=colima-knowgo；Docker Engine 29.5.2/arm64 可响应，VM为Ubuntu24.04.4、vz。
- hello-world 拉取失败根因已查明：guest /etc/resolv.conf 是指向不存在 /run/systemd/resolve/stub-resolv.conf 的链接，dnsmasq因此启动失败；非应用代码错误。
- 当前以 Colima 支持的 --dns 223.5.5.5 --dns 1.1.1.1 设置仅此VM的DNS并重启，执行会话17548。完成后再验证实际容器；尚不能称 Docker 拉取/运行测试通过。

## 最终验证：2026-10-24 18:28

历史排查过程按发生顺序保留，上文“进行中/尚未验证”均为当时状态。当前：官方 VM 镜像 SHA-256/SHA-512 通过；Colima knowgo 已启动；Engine 29.5.2、CLI 29.9.2、Compose 5.6.1；官方 hello-world 拉取并运行退出 0。DNS 缺失链接已修复并保存 provision；daemon 代理使用现有本机 7897，经 VM 网关 192.168.5.2，重启后配置生效。HTTP 四路径与 uv lock --check 再次通过。结果已写入桌面 环境验证.json。用户练习和理解检查仍未完成。
