"""
用户模型示例

这是一个完整的用户模型示例，展示如何使用 BaseModel 创建业务模型。
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class User(BaseModel):
    """
    用户模型
    
    继承自 BaseModel，自动包含 id、created_at、updated_at 字段。
    
    示例：
        ```python
        from app.models.user import User
        from app.db.session import get_db_session
        
        db = get_db_session()
        user = User(name="张三", email="zhangsan@example.com")
        db.add(user)
        db.commit()
        ```
    """
    
    __tablename__ = "users"
    
    # 用户名
    name = Column(
        String(100),
        nullable=False,
        comment="用户名",
        index=True,  # 添加索引以提高查询性能
    )
    
    # 邮箱（唯一）
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="邮箱地址",
        index=True,  # 添加索引以提高查询性能
    )
    
    # 年龄（可选）
    age = Column(
        Integer,
        nullable=True,
        comment="年龄",
    )
    
    # 是否激活
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活",
        index=True,  # 添加索引以提高查询性能
    )
    
    # 最后登录时间（可选）
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间",
    )
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

