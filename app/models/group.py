"""
群组模型

定义群组表的数据模型，用于存储群组信息。
"""

from sqlalchemy import Column, String, Text, Index
from app.db.base import BaseModel


class Group(BaseModel):
    """
    群组模型
    
    用于存储群组信息，包括群组名称、描述和创建人。
    继承自 BaseModel，自动包含 id、created_at、updated_at 字段。
    
    示例：
        ```python
        from app.models.group import Group
        from app.db.session import get_db_session
        
        db = get_db_session()
        group = Group(
            group_id="group_001",
            group_name="医疗咨询群",
            description="患者和医生的咨询群组",
            created_by="user_001"
        )
        db.add(group)
        db.commit()
        ```
    """
    
    __tablename__ = "groups"
    
    # 群组唯一标识
    group_id = Column(
        String(64),
        unique=True,
        nullable=False,
        comment="群组唯一标识",
    )
    
    # 群组名称
    group_name = Column(
        String(128),
        nullable=False,
        comment="群组名称",
    )
    
    # 群组描述
    description = Column(
        Text,
        nullable=True,
        comment="群组描述",
    )
    
    # 创建人ID
    created_by = Column(
        String(48),
        nullable=False,
        comment="创建人ID",
    )
    
    # 添加索引以提高查询性能
    __table_args__ = (
        Index("idx_group_id", "group_id"),
        Index("idx_created_by", "created_by"),
    )
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        return f"<Group(id={self.id}, group_id='{self.group_id}', group_name='{self.group_name}', created_by='{self.created_by}')>"
