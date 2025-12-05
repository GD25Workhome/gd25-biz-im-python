"""
数据库连接模块

提供 SQLAlchemy Engine 的创建和配置，支持连接池管理和健康检查。
"""

from typing import Optional
from sqlalchemy import create_engine, Engine, event
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine as EngineType

from app.config import settings


# 全局数据库引擎实例
_engine: Optional[Engine] = None


def get_engine(allow_placeholder: bool = False) -> Engine:
    """
    获取数据库引擎实例（单例模式）
    
    Args:
        allow_placeholder: 如果为 True，当 database_url 未配置时使用占位符 URL（仅用于生成迁移脚本）
    
    Returns:
        Engine: SQLAlchemy 数据库引擎实例
        
    Raises:
        ValueError: 当数据库 URL 配置无效时抛出
    """
    global _engine
    
    if _engine is None:
        database_url = settings.get_database_url_sync(allow_placeholder=allow_placeholder)
        
        # 创建引擎，配置连接池
        _engine = create_engine(
            database_url,
            # 连接池配置
            poolclass=QueuePool,
            pool_size=5,  # 连接池大小
            max_overflow=10,  # 最大溢出连接数
            pool_pre_ping=True,  # 连接前 ping，确保连接有效
            pool_recycle=3600,  # 连接回收时间（秒），1小时
            echo=settings.debug,  # 调试模式下打印 SQL 语句
        )
        
        # 注册连接事件监听器（可选，用于日志记录）
        if settings.debug:
            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                """连接建立时的回调（可用于设置数据库参数）"""
                pass
            
            @event.listens_for(_engine, "checkout")
            def receive_checkout(dbapi_conn, connection_record, connection_proxy):
                """从连接池获取连接时的回调"""
                pass
    
    return _engine


def close_engine() -> None:
    """
    关闭数据库引擎（应用关闭时调用）
    
    注意：此方法会关闭所有数据库连接，通常在应用关闭时调用。
    """
    global _engine
    
    if _engine is not None:
        _engine.dispose()
        _engine = None


def check_connection() -> bool:
    """
    检查数据库连接是否正常
    
    Returns:
        bool: 连接正常返回 True，否则返回 False
    """
    try:
        from sqlalchemy import text
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception:
        return False


# 导出引擎实例（用于直接访问）
# 注意：直接使用 get_engine() 函数获取引擎实例
# 延迟创建引擎，避免在导入时就尝试连接数据库
# engine = get_engine()  # 注释掉，改为按需调用 get_engine()

