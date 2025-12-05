# gd25-biz-im-python

轻量级 IM 服务 - 基于 FastAPI 的即时通讯系统

## 项目简介

本项目是一个轻量级即时通讯（IM）服务，主要面向独立开发者，提供用户消息发送和 AI 自动回复功能。

**重要**：本项目基于 `gd25-arch-backend-python` 脚手架开发。

## 脚手架依赖

### 脚手架项目信息

- **脚手架项目路径**：`/Users/m684620/work/github_GD25/gd25-arch-backend-python`
- **脚手架状态**：✅ 已完成开发，包含完整功能
- **脚手架功能**：
  - ✅ FastAPI 应用框架
  - ✅ SQLAlchemy ORM + Alembic 迁移
  - ✅ Repository 模式（CRUD + 分页）
  - ✅ WebSocket 支持
  - ✅ Celery 任务队列
  - ✅ 配置管理（Pydantic Settings）
  - ✅ 日志工具
  - ✅ ID 生成器
  - ✅ 依赖注入框架
  - ✅ 用户管理示例代码（完整示例）

### 脚手架提供的模块

以下模块由脚手架提供，**无需重复开发**：

| 模块 | 说明 | 文件路径 |
|------|------|----------|
| 配置管理 | 环境变量、配置验证 | `app/config.py` |
| 数据库连接 | SQLAlchemy Engine、连接池 | `app/db/database.py` |
| 基础模型 | BaseModel（id, created_at, updated_at） | `app/db/base.py` |
| 会话管理 | 数据库会话、依赖注入 | `app/db/session.py` |
| Repository 基类 | 通用 CRUD、分页查询 | `app/repositories/base.py` |
| 日志工具 | JSON/Text 格式日志 | `app/utils/logger.py` |
| ID 生成器 | 消息ID、记录ID生成 | `app/utils/id_generator.py` |
| 异常处理 | 自定义异常类 | `app/utils/exceptions.py` |
| 响应工具 | 统一响应格式 | `app/utils/response.py` |
| 依赖注入 | 数据库、认证、权限框架 | `app/dependencies.py` |
| 主应用入口 | FastAPI 应用、中间件、异常处理 | `app/main.py` |
| Celery 配置 | 任务队列配置 | `app/tasks/celery_app.py` |
| WebSocket 管理器 | 连接管理、消息推送 | `app/websocket/manager.py` |

## 快速开始

### ✅ CookieCutter 支持说明

**好消息**：脚手架项目 `gd25-arch-backend-python` **已经支持 CookieCutter 模板**！

脚手架项目包含完整的 CookieCutter 模板，位于 `cookiecutter-gd25-arch-backend-python/` 目录。

**CookieCutter 的优势：**
- ✅ 交互式配置项目参数（项目名、包名等）
- ✅ 自动替换项目中的变量（如 `{{cookiecutter.project_name}}`）
- ✅ 符合 Python 社区最佳实践
- ✅ 支持模板参数化（可选模块、数据库类型等）
- ✅ 一键生成完整项目结构

**详细验证报告**：请查看 [脚手架CookieCutter验证报告.md](./脚手架CookieCutter验证报告.md)

---

### 方式一：使用 CookieCutter 模板（⭐ 强烈推荐）

**这是最推荐的方式**，可以快速生成项目，自动替换所有变量。

```bash
# 1. 安装 CookieCutter
pip install cookiecutter

# 2. 使用脚手架模板创建项目
cookiecutter /Users/m684620/work/github_GD25/gd25-arch-backend-python/cookiecutter-gd25-arch-backend-python

# 或使用相对路径（从脚手架项目目录）
cd /Users/m684620/work/github_GD25/gd25-arch-backend-python
cookiecutter cookiecutter-gd25-arch-backend-python

# 3. 按照提示输入项目信息（交互式）
# project_name [my-project]: gd25-biz-im-python
# project_description [FastAPI 后端项目]: 轻量级 IM 服务
# author_name [GD25 Team]: Your Name
# author_email [team@gd25.com]: your.email@example.com
# python_version [3.10]: 3.10
# include_celery [y]: y          # 是否包含 Celery（输入 y 或 n）
# include_websocket [n]: y       # 是否包含 WebSocket（输入 y 或 n）
# database_type [postgresql]: postgresql

# 4. 进入生成的项目目录
cd gd25-biz-im-python

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，至少配置 DATABASE_URL

# 6. 安装依赖并启动
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 7. 初始化数据库（可选）
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 8. 启动应用
uvicorn app.main:app --reload
```

**CookieCutter 模板配置项说明**：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `project_name` | 项目名称（将作为目录名） | my-project |
| `project_description` | 项目描述 | FastAPI 后端项目 |
| `author_name` | 作者名称 | GD25 Team |
| `author_email` | 作者邮箱 | team@gd25.com |
| `python_version` | Python 版本 | 3.10 |
| `include_celery` | 是否包含 Celery 模块（y/n） | y |
| `include_websocket` | 是否包含 WebSocket 模块（y/n） | n |
| `database_type` | 数据库类型 | postgresql |

**非交互式使用（使用配置文件）**：

```bash
# 创建配置文件
cat > my-config.json << EOF
{
  "project_name": "gd25-biz-im-python",
  "project_description": "轻量级 IM 服务",
  "author_name": "Your Name",
  "author_email": "your.email@example.com",
  "python_version": "3.10",
  "include_celery": "y",
  "include_websocket": "y",
  "database_type": "postgresql"
}
EOF

# 使用配置文件生成项目（非交互式）
cookiecutter cookiecutter-gd25-arch-backend-python --config-file my-config.json --no-input
```

**更多信息**：
- 详细使用指南：`/Users/m684620/work/github_GD25/gd25-arch-backend-python/docs/边做边学/CookieCutter使用指南.md`
- 模板说明：`/Users/m684620/work/github_GD25/gd25-arch-backend-python/cookiecutter-gd25-arch-backend-python/README.md`

---

### 方式二：从脚手架复制代码（备选方案）

如果不想使用 CookieCutter，也可以手动复制脚手架代码：

```bash
# 1. 进入脚手架项目目录
cd /Users/m684620/work/github_GD25/gd25-arch-backend-python

# 2. 复制脚手架代码到当前项目
cp -r app /Users/m684620/work/github_GD25/gd25-biz-im-python/
cp -r alembic /Users/m684620/work/github_GD25/gd25-biz-im-python/
cp -r tests /Users/m684620/work/github_GD25/gd25-biz-im-python/
cp -r scripts /Users/m684620/work/github_GD25/gd25-biz-im-python/
cp requirements.txt /Users/m684620/work/github_GD25/gd25-biz-im-python/
cp requirements-dev.txt /Users/m684620/work/github_GD25/gd25-biz-im-python/
cp pytest.ini /Users/m684620/work/github_GD25/gd25-biz-im-python/
cp alembic.ini /Users/m684620/work/github_GD25/gd25-biz-im-python/
cp pyproject.toml /Users/m684620/work/github_GD25/gd25-biz-im-python/
cp .env.example /Users/m684620/work/github_GD25/gd25-biz-im-python/

# 3. 进入当前项目目录
cd /Users/m684620/work/github_GD25/gd25-biz-im-python

# 4. 创建 .env 文件
cp .env.example .env

# 5. 编辑 .env 文件，配置数据库连接等
# 至少需要配置 DATABASE_URL

# 6. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 7. 初始化数据库（可选，如果有业务模型）
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 8. 启动应用
uvicorn app.main:app --reload
```

### 方式三：使用符号链接（开发阶段推荐）

如果脚手架和本项目在同一台机器上，可以使用符号链接共享代码：

```bash
# 1. 进入当前项目目录
cd /Users/m684620/work/github_GD25/gd25-biz-im-python

# 2. 创建符号链接（仅链接脚手架的核心模块）
ln -s /Users/m684620/work/github_GD25/gd25-arch-backend-python/app/config.py app/
ln -s /Users/m684620/work/github_GD25/gd25-arch-backend-python/app/db app/
ln -s /Users/m684620/work/github_GD25/gd25-arch-backend-python/app/utils app/
ln -s /Users/m684620/work/github_GD25/gd25-arch-backend-python/app/dependencies.py app/
ln -s /Users/m684620/work/github_GD25/gd25-arch-backend-python/app/repositories/base.py app/repositories/

# 注意：main.py 需要根据项目需求修改，建议复制后修改
```

### 方式四：Git Submodule（长期维护推荐）

```bash
# 1. 将脚手架添加为 Git Submodule
cd /Users/m684620/work/github_GD25/gd25-biz-im-python
git submodule add <脚手架仓库URL> scaffold

# 2. 复制需要的文件
cp -r scaffold/app/* app/
cp -r scaffold/alembic ./
cp scaffold/requirements.txt ./
# ... 其他文件

# 3. 更新 submodule（当脚手架更新时）
git submodule update --remote scaffold
```

## 项目结构

```
gd25-biz-im-python/
├── app/                    # 应用主目录（从脚手架复制）
│   ├── api/               # API 路由（业务代码）
│   │   ├── message.py     # 消息 API（待开发）
│   │   └── ai.py          # AI API（待开发）
│   ├── services/          # 业务逻辑层（业务代码）
│   │   ├── message_service.py  # 消息服务（待开发）
│   │   └── ai_service.py        # AI 服务（待开发）
│   ├── models/            # 数据模型（业务代码）
│   │   ├── message.py     # 消息模型（待开发）
│   │   └── ai_chat_record.py    # AI 聊天记录模型（待开发）
│   ├── schemas/           # Pydantic 模式（业务代码）
│   │   ├── message.py     # 消息 Schema（待开发）
│   │   └── ai.py          # AI Schema（待开发）
│   ├── repositories/      # 数据访问层（业务代码）
│   │   ├── message_repository.py  # 消息 Repository（待开发）
│   │   └── ai_chat_repository.py   # AI Repository（待开发）
│   ├── tasks/             # Celery 任务（业务代码）
│   │   └── ai_reply_task.py       # AI 回复任务（待开发）
│   ├── websocket/         # WebSocket 处理（业务代码）
│   │   └── handler.py     # WebSocket 处理器（待开发）
│   ├── db/                # 数据库相关（脚手架提供）
│   ├── utils/             # 工具类（脚手架提供）
│   ├── config.py          # 配置管理（脚手架提供，可扩展）
│   └── main.py            # 应用入口（脚手架提供，可修改）
├── tests/                 # 测试文件（从脚手架复制）
├── alembic/               # 数据库迁移（从脚手架复制）
├── im开发文档/            # 项目文档
├── requirements.txt       # 核心依赖（从脚手架复制，需添加 LangChain 等）
├── requirements-dev.txt   # 开发依赖（从脚手架复制）
└── .env                   # 环境变量（需配置）
```

## 开发指南

### 1. 扩展配置

在 `app/config.py` 中扩展配置，添加 AI 相关配置：

```python
from app.config import Settings
from pydantic import Field

class IMSettings(Settings):
    """IM 项目自定义配置"""
    # AI 相关配置
    ai_provider: str = Field(default="openai", description="AI 服务提供商")
    ai_api_key: str = Field(..., description="AI API 密钥")
    ai_base_url: Optional[str] = Field(default=None, description="AI API 基础 URL")
    ai_model: str = Field(default="gpt-3.5-turbo", description="AI 模型名称")
    ai_temperature: float = Field(default=0.7, ge=0, le=2, description="AI 温度参数")
    ai_max_tokens: int = Field(default=1000, ge=1, description="AI 最大 token 数")

settings = IMSettings()
```

### 2. 创建业务模型

参考脚手架中的 `app/models/user.py`，创建业务模型：

```python
from app.db.base import BaseModel
from sqlalchemy import Column, String, Text, Integer, ForeignKey

class Message(BaseModel):
    """消息模型"""
    __tablename__ = "messages"
    
    user_id = Column(Integer, nullable=False, comment="用户ID")
    content = Column(Text, nullable=False, comment="消息内容")
    # ... 其他字段
```

### 3. 创建 Repository

继承脚手架提供的 `BaseRepository`：

```python
from app.repositories.base import BaseRepository
from app.models.message import Message
from sqlalchemy.orm import Session

class MessageRepository(BaseRepository[Message]):
    """消息 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(Message, db)
    
    # 可以添加自定义查询方法
    def get_by_user_id(self, user_id: int):
        return self.filter_by(user_id=user_id)
```

### 4. 创建 Service

```python
from app.services.message_service import MessageService
from app.repositories.message_repository import MessageRepository
from sqlalchemy.orm import Session

class MessageService:
    """消息服务"""
    
    def __init__(self, db: Session):
        self.repository = MessageRepository(db)
    
    def create_message(self, user_id: int, content: str):
        # 业务逻辑
        return self.repository.create({"user_id": user_id, "content": content})
```

### 5. 创建 API 路由

参考脚手架中的 `app/api/users.py`，创建业务 API：

```python
from fastapi import APIRouter, Depends
from app.dependencies import get_db
from app.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["消息"])

@router.post("/")
async def create_message(
    message_data: MessageCreate,
    service: MessageService = Depends(lambda db: MessageService(db)),
):
    # API 逻辑
    pass
```

### 6. 注册路由

在 `app/main.py` 中注册业务路由：

```python
from app.api import message, ai

app.include_router(message.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
```

## CookieCutter 模板说明

脚手架项目已经包含完整的 CookieCutter 模板，位于 `cookiecutter-gd25-arch-backend-python/` 目录。

### 模板结构

```
gd25-arch-backend-python/
├── cookiecutter.json                                    # 根配置文件
└── cookiecutter-gd25-arch-backend-python/              # 模板目录
    ├── cookiecutter.json                                # 模板配置文件
    ├── README.md                                        # 模板说明
    ├── hooks/                                           # 后处理脚本
    │   └── post_gen_project.py                         # 生成后执行的脚本
    └── {{ cookiecutter.project_name }}/                # 模板文件目录
        ├── app/                                         # 应用代码
        ├── tests/                                       # 测试代码
        ├── alembic/                                     # 数据库迁移
        ├── requirements.txt                             # 依赖文件
        ├── pyproject.toml                               # 项目配置
        └── README.md                                    # 项目文档
```

### 模板特性

- ✅ **变量替换**：自动替换项目名称、作者信息等
- ✅ **可选模块**：支持选择是否包含 Celery、WebSocket 等模块
- ✅ **后处理脚本**：自动清理不需要的文件
- ✅ **完整文档**：包含详细的使用说明

### 验证报告

详细的验证报告请查看：[脚手架CookieCutter验证报告.md](./脚手架CookieCutter验证报告.md)

---

## 脚手架更新同步

如果脚手架有更新，需要同步到本项目：

```bash
# 1. 进入脚手架项目
cd /Users/m684620/work/github_GD25/gd25-arch-backend-python

# 2. 拉取最新代码
git pull

# 3. 复制更新的文件到当前项目
cp app/config.py /Users/m684620/work/github_GD25/gd25-biz-im-python/app/
cp app/db/* /Users/m684620/work/github_GD25/gd25-biz-im-python/app/db/
# ... 其他更新的文件

# 4. 检查是否有冲突，解决冲突后测试
```

## 详细文档

- [项目总体设计](./im开发文档/01-项目总体设计.md)
- [模块详细设计](./im开发文档/02-模块详细设计.md)
- [API 接口文档](./im开发文档/03-API接口文档.md)
- [开发计划](./im开发文档/04-开发计划.md)
- [脚手架模块分析](./im开发文档/05-脚手架模块分析.md)

## 许可证

MIT License
