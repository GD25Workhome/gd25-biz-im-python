# Alembic 数据库迁移工具使用指南

## 一、Alembic 工作原理

### 1.1 什么是 Alembic？

Alembic 是 SQLAlchemy 官方提供的数据库迁移工具，用于管理数据库 schema 的版本变更。它允许你：

- **版本控制数据库结构**：像 Git 管理代码一样管理数据库 schema
- **自动生成迁移脚本**：基于 SQLAlchemy 模型自动生成迁移文件
- **安全地升级/降级**：支持向前和向后迁移，可以回滚到任意版本
- **团队协作**：多人开发时统一管理数据库变更

### 1.2 核心概念

#### 1.2.1 迁移脚本（Migration Script）

迁移脚本是 Python 文件，包含两个核心函数：

- `upgrade()`：执行升级操作（向前迁移）
- `downgrade()`：执行降级操作（向后回滚）

每个迁移脚本都有一个唯一的 **revision ID**（如 `25c8f48abee5`），用于标识版本。

#### 1.2.2 版本链（Version Chain）

Alembic 通过 `down_revision` 字段建立版本之间的链式关系：

```
初始版本 (None) 
    ↓
25c8f48abee5 (创建初始表)
    ↓
下一个版本 (revision_id)
    ↓
...
```

#### 1.2.3 版本表（alembic_version）

Alembic 在数据库中维护一个 `alembic_version` 表，记录当前数据库的版本号：

```sql
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);
```

### 1.3 工作流程

```
1. 修改 SQLAlchemy 模型
   ↓
2. 运行 alembic revision --autogenerate
   ↓
3. Alembic 比较模型与数据库差异
   ↓
4. 生成迁移脚本（upgrade/downgrade）
   ↓
5. 检查并编辑迁移脚本（可选）
   ↓
6. 运行 alembic upgrade head 执行迁移
   ↓
7. 数据库结构更新完成
```

## 二、项目中的 Alembic 配置

### 2.1 目录结构

```
alembic/
├── env.py              # Alembic 环境配置（核心文件）
├── README.md           # 使用说明
├── script.py.mako      # 迁移脚本模板
└── versions/           # 迁移脚本目录
    ├── .gitkeep
    └── 20251210_1554_25c8f48abee5_create_initial_tables.py

alembic.ini             # Alembic 主配置文件
```

### 2.2 核心配置文件解析

#### 2.2.1 `alembic.ini`

```ini
[alembic]
# 迁移脚本目录
script_location = alembic

# 迁移脚本文件名模板
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
# 生成的文件名示例：20251210_1554_25c8f48abee5_create_initial_tables.py

# 数据库 URL（通常从 env.py 动态设置，不在这里硬编码）
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

#### 2.2.2 `alembic/env.py`（关键配置）

这个文件是 Alembic 的核心配置，主要做了以下几件事：

**① 导入项目路径和配置**
```python
# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 导入配置和基础模型
from app.config import settings
from app.db.base import Base
```

**② 导入所有模型类**
```python
# 必须导入所有模型，否则 Alembic 无法检测到它们
from app.models import User, Group, GroupMember, Message, AIInteractionRecord
```

**为什么必须导入所有模型？**

Alembic 的 `autogenerate` 功能通过比较以下两者来生成迁移脚本：
- **当前数据库的 schema**（从数据库读取）
- **SQLAlchemy 模型的 metadata**（从 `Base.metadata` 读取）

如果模型类没有被导入，Python 不会执行类定义，模型就不会注册到 `Base.metadata` 中，Alembic 就检测不到这些表。

**③ 设置目标元数据**
```python
target_metadata = Base.metadata
```

这告诉 Alembic 使用哪个 metadata 对象来比较差异。

**④ 设置数据库 URL**
```python
database_url = settings.get_database_url_sync(allow_placeholder=True)
config.set_main_option("sqlalchemy.url", database_url)
```

从项目配置中读取数据库连接 URL。`allow_placeholder=True` 允许在生成迁移脚本时使用占位符 URL（不需要实际连接数据库）。

**⑤ 定义迁移执行函数**

- `run_migrations_offline()`：离线模式，生成 SQL 脚本但不执行
- `run_migrations_online()`：在线模式，直接执行迁移

### 2.3 项目中的特殊处理

#### 2.3.1 占位符配置

在 `env.py` 中有这样的代码：

```python
# 注意：在生成迁移脚本时，如果配置缺失，使用占位符值
if not os.getenv("AI_SERVICE_URL"):
    os.environ["AI_SERVICE_URL"] = "http://placeholder.ai"
if not os.getenv("AI_SERVICE_API_KEY"):
    os.environ["AI_SERVICE_API_KEY"] = "placeholder_key"
```

这是因为项目的 `IMSettings` 要求 `ai_service_url` 和 `ai_service_api_key` 必须配置。但在生成迁移脚本时，我们可能不需要这些配置，所以使用占位符值。

#### 2.3.2 索引创建的特殊处理

在迁移脚本中，你会看到这样的代码：

```python
def index_exists(index_name: str) -> bool:
    """检查索引是否存在"""
    result = connection.execute(
        sql_text("""
            SELECT 1 FROM pg_indexes 
            WHERE indexname = :index_name
        """),
        {"index_name": index_name}
    )
    return result.fetchone() is not None

def create_index_if_not_exists(index_name: str, table_name: str, columns: list, **kwargs):
    """如果索引不存在则创建"""
    if not index_exists(index_name):
        op.create_index(index_name, table_name, columns, **kwargs)
```

这是因为在迁移过程中，如果索引已存在，直接创建会报错。这个辅助函数确保幂等性（可以安全地重复执行）。

## 三、常用命令

### 3.1 查看当前状态

```bash
# 查看当前数据库版本
alembic current

# 查看迁移历史
alembic history

# 查看迁移历史（详细，包含分支信息）
alembic history --verbose
```

### 3.2 生成迁移脚本

```bash
# 自动生成迁移脚本（推荐）
# Alembic 会比较模型和数据库的差异，自动生成迁移代码
alembic revision --autogenerate -m "描述信息"

# 创建空迁移脚本（手动编写迁移逻辑）
alembic revision -m "描述信息"
```

**示例：**
```bash
# 添加了新字段后
alembic revision --autogenerate -m "add_user_email_field"

# 生成的文件：20251210_1600_abc123def456_add_user_email_field.py
```

### 3.3 执行迁移

```bash
# 升级到最新版本（最常用）
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision_id>
# 例如：alembic upgrade 25c8f48abee5

# 升级一个版本
alembic upgrade +1

# 降级一个版本
alembic downgrade -1

# 降级到指定版本
alembic downgrade <revision_id>

# 降级到基础版本（删除所有表，危险操作！）
alembic downgrade base
```

### 3.4 其他有用命令

```bash
# 查看升级到指定版本需要执行的迁移
alembic upgrade <revision_id> --sql

# 查看降级到指定版本需要执行的 SQL
alembic downgrade <revision_id> --sql

# 生成 SQL 脚本但不执行（离线模式）
alembic upgrade head --sql > migration.sql
```

## 四、实际使用场景

### 4.1 场景一：添加新模型

**步骤：**

1. **创建模型文件** `app/models/new_model.py`：
```python
from app.db.base import BaseModel
from sqlalchemy import Column, String

class NewModel(BaseModel):
    __tablename__ = "new_models"
    
    name = Column(String(100), nullable=False)
    description = Column(String(500))
```

2. **在 `app/models/__init__.py` 中导出**：
```python
from app.models.new_model import NewModel

__all__ = ["User", "Group", "Message", "NewModel"]  # 添加 NewModel
```

3. **在 `alembic/env.py` 中导入**：
```python
from app.models import User, Group, GroupMember, Message, AIInteractionRecord, NewModel
```

4. **生成迁移脚本**：
```bash
alembic revision --autogenerate -m "add_new_model_table"
```

5. **检查生成的迁移脚本**（重要！）：
```python
def upgrade() -> None:
    op.create_table('new_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('new_models')
```

6. **执行迁移**：
```bash
alembic upgrade head
```

### 4.2 场景二：修改现有模型

**示例：给 User 表添加 email 字段**

1. **修改模型** `app/models/user.py`：
```python
class User(BaseModel):
    __tablename__ = "users"
    
    user_id = Column(String(48), unique=True, nullable=False)
    username = Column(String(64), nullable=False)
    user_role = Column(String(32), nullable=False)
    email = Column(String(255), nullable=True)  # 新增字段
```

2. **生成迁移脚本**：
```bash
alembic revision --autogenerate -m "add_user_email_field"
```

3. **检查生成的脚本**（可能需要手动调整）：
```python
def upgrade() -> None:
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'email')
```

4. **如果字段不能为 NULL，需要分步迁移**：
```python
def upgrade() -> None:
    # 第一步：添加可为 NULL 的字段
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=True))
    
    # 第二步：填充默认值（如果需要）
    # op.execute("UPDATE users SET email = '' WHERE email IS NULL")
    
    # 第三步：设置为 NOT NULL（如果需要）
    # op.alter_column('users', 'email', nullable=False)

def downgrade() -> None:
    op.drop_column('users', 'email')
```

5. **执行迁移**：
```bash
alembic upgrade head
```

### 4.3 场景三：添加索引

**方法一：在模型中定义（推荐）**

```python
from sqlalchemy import Index

class Message(BaseModel):
    __tablename__ = "messages"
    
    message_id = Column(String(64), unique=True, nullable=False)
    group_id = Column(String(64), nullable=False)
    
    # 在模型中定义索引
    __table_args__ = (
        Index('idx_message_group_created', 'group_id', 'created_at'),
    )
```

然后运行 `alembic revision --autogenerate`。

**方法二：手动编写迁移脚本**

```python
def upgrade() -> None:
    op.create_index('idx_message_group_created', 'messages', ['group_id', 'created_at'])

def downgrade() -> None:
    op.drop_index('idx_message_group_created', table_name='messages')
```

### 4.4 场景四：数据迁移（需要手动编写）

如果需要在迁移过程中迁移数据，需要手动编写迁移脚本：

```bash
alembic revision -m "migrate_user_data"
```

```python
def upgrade() -> None:
    # 1. 添加新字段
    op.add_column('users', sa.Column('full_name', sa.String(length=200), nullable=True))
    
    # 2. 迁移数据
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET full_name = username WHERE full_name IS NULL")
    )
    
    # 3. 设置为 NOT NULL（如果需要）
    op.alter_column('users', 'full_name', nullable=False)

def downgrade() -> None:
    op.drop_column('users', 'full_name')
```

## 五、最佳实践

### 5.1 迁移脚本检查清单

在提交迁移脚本前，确保：

- ✅ **检查自动生成的脚本**：Alembic 可能遗漏某些变更，需要手动补充
- ✅ **测试升级和降级**：确保 `upgrade()` 和 `downgrade()` 都能正常工作
- ✅ **处理数据迁移**：如果涉及数据变更，确保迁移逻辑正确
- ✅ **处理外键约束**：添加/删除外键时注意顺序
- ✅ **处理索引**：确保索引创建/删除不会失败（使用 `IF NOT EXISTS` 或检查函数）

### 5.2 团队协作规范

1. **迁移脚本必须提交到版本控制**（Git）
2. **不要修改已执行的迁移脚本**：如果发现错误，创建新的迁移脚本修复
3. **迁移脚本命名要清晰**：使用有意义的描述，如 `add_user_email_field` 而不是 `update1`
4. **在合并前同步**：合并代码前先执行 `alembic upgrade head` 确保数据库是最新的

### 5.3 生产环境注意事项

1. **备份数据库**：执行迁移前必须备份
2. **在测试环境先验证**：确保迁移脚本在测试环境正常运行
3. **使用事务**：Alembic 默认在事务中执行，失败会自动回滚
4. **监控执行时间**：大表迁移可能需要较长时间，注意超时设置
5. **准备回滚方案**：了解如何快速回滚到上一个版本

### 5.4 常见问题处理

#### 问题 1：Alembic 检测不到模型变更

**原因：**
- 模型类没有被导入到 `alembic/env.py`
- 模型没有继承 `Base` 或 `BaseModel`
- 模型没有正确定义 `__tablename__`

**解决：**
1. 检查 `alembic/env.py` 是否导入了所有模型
2. 检查模型类定义是否正确

#### 问题 2：迁移脚本执行失败

**常见原因：**
- 数据库连接失败（检查 `DATABASE_URL` 环境变量）
- 表/字段已存在（使用 `IF NOT EXISTS` 或检查函数）
- 外键约束冲突（注意创建/删除顺序）
- 数据不满足约束（如 NOT NULL 字段有 NULL 值）

**解决：**
1. 查看完整错误信息
2. 检查数据库当前状态：`alembic current`
3. 手动修复数据库或调整迁移脚本

#### 问题 3：需要回滚迁移

```bash
# 查看历史
alembic history

# 回滚到上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>
```

## 六、项目中的迁移脚本示例

查看项目中的实际迁移脚本：

```bash
cat alembic/versions/20251210_1554_25c8f48abee5_create_initial_tables.py
```

这个脚本展示了：
- 创建多个表（users, groups, messages 等）
- 创建索引（带检查函数，避免重复创建）
- 删除旧表（从其他项目迁移过来的表）
- 完整的 `upgrade()` 和 `downgrade()` 函数

## 七、总结

Alembic 是管理数据库 schema 变更的强大工具。在这个项目中：

1. **配置已就绪**：`alembic/env.py` 已正确配置，会自动检测模型变更
2. **使用流程**：修改模型 → 生成迁移 → 检查脚本 → 执行迁移
3. **注意事项**：
   - 新增模型必须在 `env.py` 中导入
   - 检查自动生成的脚本
   - 生产环境执行前备份数据库

**快速参考：**

```bash
# 日常开发流程
alembic revision --autogenerate -m "描述"  # 生成迁移
alembic upgrade head                       # 执行迁移
alembic current                            # 查看当前版本
alembic history                            # 查看历史
alembic downgrade -1                       # 回滚一个版本
```
