"""
基础模型模块

提供基础模型类和 DeclarativeBase，所有数据模型都应继承自 BaseModel。
"""

from datetime import datetime
from typing import Any
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    SQLAlchemy DeclarativeBase
    
    所有数据模型的基类，提供表名自动生成等功能。
    """
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        自动生成表名
        
        将类名转换为下划线命名的小写表名。
        例如：UserModel -> user_model
        
        Returns:
            str: 表名
        """
        # 将驼峰命名转换为下划线命名
        import re
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        # 如果类名以 Model 结尾，去掉 Model
        if name.endswith('_model'):
            name = name[:-6]
        return name


class BaseModel(Base):
    """
    基础模型类
    
    所有业务模型都应继承此类，自动包含以下字段：
    - id: 主键（自增整数）
    - created_at: 创建时间
    - updated_at: 更新时间
    
    示例：
        ```python
        from app.db.base import BaseModel
        from sqlalchemy import Column, String
        
        class User(BaseModel):
            __tablename__ = "users"
            
            name = Column(String(100), nullable=False)
            email = Column(String(255), unique=True, nullable=False)
        ```
    """
    
    __abstract__ = True  # 标记为抽象类，不会创建对应的表
    
    # 主键
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="主键ID",
    )
    
    # 创建时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    
    # 更新时间
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )
    
    def to_dict(self) -> dict[str, Any]:
        """
        将模型实例转换为字典
        
        Returns:
            dict: 包含模型字段的字典
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"

