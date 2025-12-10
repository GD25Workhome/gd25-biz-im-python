"""
群组成员模型

定义群组成员表的数据模型，用于存储群组成员信息和用户在群组中的身份标签。
"""

from sqlalchemy import Column, String, DateTime, Index, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import BaseModel


class GroupMember(BaseModel):
    """
    群组成员模型
    
    用于存储群组成员信息，包括用户在群组中的身份标签。
    继承自 BaseModel，自动包含 id、created_at、updated_at 字段。
    
    重要说明：
    - user_role 字段表示用户在群组中的身份，可能与用户在系统中的全局身份（User.user_role）不同
    - 例如：一个医生用户可以在某个群组中被标记为"患者"身份
    
    示例：
        ```python
        from app.models.group_member import GroupMember
        from app.db.session import get_db_session
        
        db = get_db_session()
        member = GroupMember(
            group_id="group_001",
            user_id="user_001",
            user_role="PATIENT"
        )
        db.add(member)
        db.commit()
        ```
    """
    
    __tablename__ = "group_members"
    
    # 群组ID
    group_id = Column(
        String(64),
        nullable=False,
        comment="群组ID",
    )
    
    # 用户ID
    user_id = Column(
        String(48),
        nullable=False,
        comment="用户ID",
    )
    
    # 用户在群组中的身份标签：PATIENT/DOCTOR/AI_ASSISTANT
    user_role = Column(
        String(32),
        nullable=False,
        comment="用户在群组中的身份标签：PATIENT/DOCTOR/AI_ASSISTANT",
    )
    
    # 加入时间
    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="加入时间",
    )
    
    # 添加联合唯一约束和索引
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uk_group_user"),
        Index("idx_group_id", "group_id"),
        Index("idx_user_id", "user_id"),
        Index("idx_user_role", "user_role"),
    )
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        return f"<GroupMember(id={self.id}, group_id='{self.group_id}', user_id='{self.user_id}', user_role='{self.user_role}')>"
