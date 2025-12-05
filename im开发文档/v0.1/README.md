# 轻量级 IM 服务 - 开发文档

## 📚 文档索引

本文档空间包含轻量级 IM 服务的完整开发文档，包括总体设计、模块详细设计、API 接口文档和开发计划。

### 文档列表

1. **[01-项目总体设计.md](./01-项目总体设计.md)**
   - 项目概述
   - 系统架构设计
   - 模块划分
   - 数据库设计
   - 技术选型

2. **[02-模块详细设计.md](./02-模块详细设计.md)**
   - 项目结构
   - 各模块详细设计
   - 代码示例
   - 实现要点

3. **[03-API接口文档.md](./03-API接口文档.md)**
   - HTTP API 接口
   - WebSocket API 接口
   - 请求/响应格式
   - 错误码说明
   - 调用示例

4. **[04-开发计划.md](./04-开发计划.md)**
   - 里程碑划分
   - 任务清单
   - 验收标准
   - 测试验证
   - 开发顺序

---

## 🎯 项目概述

### 核心功能

- ✅ 用户发送消息（WebSocket + HTTP API）
- ✅ AI 自动回复消息
- ✅ 消息存储和查询
- ✅ AI 聊天记录管理
- ✅ 实时消息推送（WebSocket）

### 技术栈

```
Python + FastAPI + LangChain + Celery + Redis + PostgreSQL
```

### 项目特点

- **轻量级**：Min 版本，只包含核心功能
- **快速开发**：使用 Python，开发效率高
- **AI 集成**：使用 LangChain，AI 生态完善
- **异步处理**：使用 Celery，支持高并发
- **实时通信**：WebSocket 支持实时推送

---

## 🚀 快速开始

### 1. 环境准备

```bash
# Python 3.10+
python --version

# PostgreSQL 14+ 或 MySQL 8.0+
psql --version

# Redis 6.0+
redis-cli --version
```

### 2. 项目初始化（使用 CookieCutter 模板）

```bash
# 1. 安装 CookieCutter
pip install cookiecutter

# 2. 使用脚手架模板生成项目
cookiecutter /Users/m684620/work/github_GD25/gd25-arch-backend-python/cookiecutter-gd25-arch-backend-python

# 3. 按提示输入项目信息
# project_name: gd25-biz-im-python
# include_celery: y
# include_websocket: y
# 其他配置按需填写

# 4. 进入生成的项目目录
cd gd25-biz-im-python

# 5. 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 6. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，配置数据库、Redis、AI 等
```

### 4. 数据库初始化

```bash
# 运行数据库迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 启动 FastAPI 服务
uvicorn app.main:app --reload

# 启动 Celery Worker（新终端）
celery -A app.tasks.celery_app worker --loglevel=info
```

### 6. 测试接口

```bash
# 健康检查
curl http://localhost:8000/health

# 发送消息
curl -X POST http://localhost:8000/api/message/send \
  -H "Content-Type: application/json" \
  -d '{"content": "你好", "session_id": "test_user"}'
```

---

## 📖 文档使用指南

### 对于开发者

1. **开始开发前**：阅读 `01-项目总体设计.md` 了解整体架构
2. **开发具体模块**：参考 `02-模块详细设计.md` 了解实现细节
3. **开发 API**：参考 `03-API接口文档.md` 了解接口规范
4. **按计划开发**：参考 `04-开发计划.md` 按里程碑推进

### 对于前端开发者

1. **API 对接**：主要参考 `03-API接口文档.md`
2. **WebSocket 对接**：参考 `03-API接口文档.md` 中的 WebSocket 部分
3. **错误处理**：参考 `03-API接口文档.md` 中的错误码说明

---

## 🔄 开发流程

### 1. 理解需求

- 阅读 `01-项目总体设计.md` 了解项目背景和需求
- 阅读 `04-开发计划.md` 了解开发计划

### 2. 开始开发

- 按照 `04-开发计划.md` 中的里程碑顺序开发
- 参考 `02-模块详细设计.md` 实现具体模块
- 参考 `03-API接口文档.md` 实现 API 接口

### 3. 测试验证

- 每个里程碑完成后进行测试验证
- 参考 `04-开发计划.md` 中的测试验证部分

### 4. 文档更新

- 代码变更时同步更新文档
- API 变更时更新 `03-API接口文档.md`

---

## 📝 开发规范

### 代码规范

- 使用 Python 类型提示（Type Hints）
- 遵循 PEP 8 代码风格
- 使用 Pydantic 进行数据验证
- 添加必要的代码注释

### 文档规范

- 代码变更时同步更新文档
- API 变更时更新 API 文档
- 重要功能添加使用示例

### 测试规范

- 每个模块编写单元测试
- 关键流程编写集成测试
- 使用 Locust 进行压测

---

## 🐛 问题反馈

如果在开发过程中遇到问题：

1. 检查文档是否已说明
2. 检查代码示例是否正确
3. 查看日志定位问题
4. 记录问题并更新文档

---

## 📅 开发进度

### 里程碑进度

- [ ] 里程碑 1：项目基础搭建
- [ ] 里程碑 2：数据模型和仓储层
- [ ] 里程碑 3：消息服务 API
- [ ] 里程碑 4：Celery 异步任务
- [ ] 里程碑 5：AI 服务集成
- [ ] 里程碑 6：WebSocket 实时通信
- [ ] 里程碑 7：AI 相关 API
- [ ] 里程碑 8：测试和优化

### 当前状态

- **项目状态**：设计阶段
- **当前里程碑**：未开始
- **预计完成时间**：3-4 周

---

## 🔗 相关文档

### 参考文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangChain 官方文档](https://python.langchain.com/)
- [Celery 官方文档](https://docs.celeryproject.org/)
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)

### 项目分析文档

- [IM服务开发方式对比分析](../im服务自己开发/IM服务开发方式对比分析.md)
- [轻量级IM服务开发方案分析](../im服务自己开发/轻量级IM服务开发方案分析.md)
- [轻量级IM自研python、java对比](../im服务自己开发/轻量级IM自研python、java对比.md)

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 项目 Issue
- 文档更新 PR

---

**文档版本**：v1.0  
**创建时间**：2025-01-27  
**最后更新**：2025-01-27

