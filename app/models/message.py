"""
消息模型

定义消息表的数据模型，用于存储用户消息和 AI 回复消息。
"""

from sqlalchemy import Column, String, Text, Index
from app.db.base import BaseModel


class Message(BaseModel):
    """
    消息模型
    
    用于存储用户发送的消息和 AI 回复的消息。
    继承自 BaseModel，自动包含 id、created_at、updated_at 字段。
    """
    
    __tablename__ = "messages"
    
    # 消息唯一标识（使用 ID 生成器生成）
    message_id = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="消息唯一标识",
    )
    
    # 会话ID（用户ID）
    session_id = Column(
        String(48),
        nullable=False,
        index=True,
        comment="会话ID（用户ID）",
    )
    
    # 发送人ID
    from_user_id = Column(
        String(48),
        nullable=False,
        index=True,
        comment="发送人ID",
    )
    
    # 消息类型：TEXT（用户消息）、AI_REPLY（AI回复）
    msg_type = Column(
        String(32),
        nullable=False,
        default="TEXT",
        comment="消息类型：TEXT/AI_REPLY",
    )
    
    # 消息内容
    msg_content = Column(
        Text,
        nullable=False,
        comment="消息内容",
    )
    
    # 添加复合索引以提高查询性能
    __table_args__ = (
        Index("idx_session_created", "session_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        return f"<Message(id={self.id}, message_id='{self.message_id}', session_id='{self.session_id}', msg_type='{self.msg_type}')>"

