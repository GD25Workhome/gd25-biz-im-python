"""
消息模型

定义消息表的数据模型，用于存储群组消息。
"""

from sqlalchemy import Column, String, Text, Index
from app.db.base import BaseModel


class Message(BaseModel):
    """
    消息模型
    
    用于存储群组消息，支持文本、图片和AI回复等消息类型。
    继承自 BaseModel，自动包含 id、created_at、updated_at 字段。
    
    重要说明：
    - 所有消息都关联到群组（group_id），不支持单聊消息
    - from_user_id 可以是普通用户ID，也可以是系统AI助手ID（如 'ai_assistant_001'）
    
    示例：
        ```python
        from app.models.message import Message
        from app.db.session import get_db_session
        
        db = get_db_session()
        message = Message(
            message_id="msg_001",
            group_id="group_001",
            from_user_id="user_001",
            msg_type="TEXT",
            msg_content="这是一条消息"
        )
        db.add(message)
        db.commit()
        ```
    """
    
    __tablename__ = "messages"
    
    # 消息唯一标识（使用 ID 生成器生成）
    message_id = Column(
        String(64),
        unique=True,
        nullable=False,
        comment="消息唯一标识",
    )
    
    # 群组ID
    group_id = Column(
        String(64),
        nullable=False,
        comment="群组ID",
    )
    
    # 发送人ID
    from_user_id = Column(
        String(48),
        nullable=False,
        comment="发送人ID",
    )
    
    # 消息类型：TEXT(文本)/IMAGE(图片)/AI_REPLY(AI回复)
    msg_type = Column(
        String(32),
        nullable=False,
        default="TEXT",
        comment="消息类型：TEXT(文本)/IMAGE(图片)/AI_REPLY(AI回复)",
    )
    
    # 消息内容
    msg_content = Column(
        Text,
        nullable=False,
        comment="消息内容",
    )
    
    # 添加索引以提高查询性能
    __table_args__ = (
        Index("idx_group_id", "group_id"),
        Index("idx_from_user_id", "from_user_id"),
        Index("idx_created_at", "created_at"),
        Index("idx_group_created", "group_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        return f"<Message(id={self.id}, message_id='{self.message_id}', group_id='{self.group_id}', msg_type='{self.msg_type}')>"

