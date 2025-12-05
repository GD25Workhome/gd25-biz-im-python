"""
数据库会话管理模块

提供数据库会话的创建、管理和依赖注入功能。
"""

from typing import Generator, Optional
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import event

from app.db.database import get_engine


# 全局会话工厂
_SessionLocal: Optional[sessionmaker[Session]] = None


def get_session_local() -> sessionmaker[Session]:
    """
    获取或创建会话工厂（单例模式）
    
    Returns:
        sessionmaker[Session]: 数据库会话工厂
    """
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    
    return _SessionLocal


# 导出会话工厂（用于直接访问）
# 延迟创建，避免在导入时就尝试连接数据库
# 注意：如果需要在导入时创建，可以调用 get_session_local(allow_placeholder=True)
# 但通常应该按需调用 get_session_local()
def _get_session_local_lazy():
    """延迟创建 SessionLocal，仅在需要时调用"""
    return get_session_local()

# 为了保持向后兼容，提供一个属性访问方式
class SessionLocalProxy:
    """SessionLocal 的代理类，延迟创建实际的 SessionLocal"""
    def __call__(self):
        return get_session_local()()
    
    def __getattr__(self, name):
        return getattr(get_session_local(), name)

SessionLocal = SessionLocalProxy()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的依赖注入函数（用于 FastAPI）
    
    此函数用于 FastAPI 的依赖注入，自动管理数据库会话的生命周期：
    - 创建会话
    - 在请求处理完成后自动提交或回滚
    - 自动关闭会话
    
    Yields:
        Session: 数据库会话实例
        
    Example:
        ```python
        from fastapi import Depends
        from app.db.session import get_db
        
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
        ```
    """
    session_local = get_session_local()
    db = session_local()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    获取数据库会话（用于非 FastAPI 场景）
    
    注意：使用此方法获取的会话需要手动管理生命周期。
    建议使用上下文管理器或 try-finally 确保会话正确关闭。
    
    Returns:
        Session: 数据库会话实例
        
    Example:
        ```python
        from app.db.session import get_db_session
        
        db = get_db_session()
        try:
            users = db.query(User).all()
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        ```
    """
    session_local = get_session_local()
    return session_local()


# 初始化会话工厂（延迟创建，避免在导入时就尝试连接数据库）
# get_session_local()  # 注释掉，改为按需调用

