"""
用户模型

定义用户表的数据模型，用于存储用户信息和用户身份标签。
"""

from sqlalchemy import Column, String, Index
from app.db.base import BaseModel


class User(BaseModel):
    """
    用户模型
    
    用于存储用户信息和用户身份标签（PATIENT/DOCTOR/AI_ASSISTANT）。
    继承自 BaseModel，自动包含 id、created_at、updated_at 字段。
    
    示例：
        ```python
        from app.models.user import User
        from app.db.session import get_db_session
        
        db = get_db_session()
        user = User(user_id="user_001", username="张三", user_role="PATIENT")
        db.add(user)
        db.commit()
        ```
    """
    
    __tablename__ = "users"
    
    # 用户唯一标识
    user_id = Column(
        String(48),
        unique=True,
        nullable=False,
        comment="用户唯一标识",
    )
    
    # 用户名
    username = Column(
        String(64),
        nullable=False,
        comment="用户名",
    )
    
    # 用户身份：PATIENT(患者)/DOCTOR(医生)/AI_ASSISTANT(医生AI助手)
    user_role = Column(
        String(32),
        nullable=False,
        default="PATIENT",
        comment="用户身份：PATIENT(患者)/DOCTOR(医生)/AI_ASSISTANT(医生AI助手)",
    )
    
    # 添加索引以提高查询性能
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_user_role", "user_role"),
    )
    
    def is_patient(self) -> bool:
        """判断是否为患者"""
        return self.user_role == "PATIENT"
    
    def is_doctor(self) -> bool:
        """判断是否为医生"""
        return self.user_role == "DOCTOR"
    
    def is_ai_assistant(self) -> bool:
        """判断是否为AI助手"""
        return self.user_role == "AI_ASSISTANT"
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        return f"<User(id={self.id}, user_id='{self.user_id}', username='{self.username}', user_role='{self.user_role}')>"

