"""
Alembic 环境配置

支持数据库迁移脚本的生成和执行。
"""

import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 导入配置和基础模型
from app.config import settings
from app.db.base import Base

# 导入所有模型，确保 Alembic 能够检测到它们
# 注意：必须导入所有模型类，否则 Alembic 无法自动生成迁移脚本
from app.models import User, Message, AIChatRecord  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 解释配置文件用于 Python 日志记录
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置目标元数据，用于 'autogenerate' 支持
# 注意：需要导入所有模型以确保 Alembic 能够检测到它们
target_metadata = Base.metadata

# 设置数据库连接 URL（从配置读取）
# 如果未配置数据库 URL，使用占位符（仅用于生成迁移脚本）
database_url = settings.get_database_url_sync(allow_placeholder=True)
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """
    在 'offline' 模式下运行迁移
    
    此模式配置上下文时只使用 URL，而不使用 Engine。
    通过跳过 Engine 创建，我们甚至不需要 DBAPI 可用。
    
    对 context.execute() 的调用会发出给定的字符串到脚本输出。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在 'online' 模式下运行迁移
    
    在此场景中，我们需要创建一个 Engine
    并将连接与上下文关联。
    """
    # 从 alembic.ini 中的配置创建引擎
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

