# 文枢本地部署 Implementation Plan

> Execute inline in this session; deployment is authorized by the user.

**Goal:** 在桌面大模型开发目录安装并启动文枢，提供可重复启停的本地环境。

**Architecture:** FastAPI + Next.js + pi 服务；MongoDB 持久化，Redis 承载会话及异步任务。默认无模型密钥时使用项目现有离线降级。

**Tech Stack:** Python venv、Node.js、MongoDB、Redis。

- [x] 解压并检查现有运行时、端口和配置。
- [x] 安装 Python/Node 依赖与 MongoDB/Redis。
- [x] 创建仅本机可访问的本地配置、启停脚本和使用说明。
- [x] 初始化部门与样例文档，启动 API、Worker、前端和 pi 服务。
- [x] 运行离线测试、构建检查，以及登录、问答、异步作业和持久化验证。
- [x] 记录访问地址、账号、模型配置边界和验证结果。
