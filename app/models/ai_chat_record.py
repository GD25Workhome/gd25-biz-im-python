"""
AI 聊天记录模型

定义 AI 聊天记录表的数据模型，用于存储 AI 回复的请求和响应记录。
"""

from sqlalchemy import Column, String, Text, Integer, BigInteger, Index
from app.db.base import BaseModel


class AIChatRecord(BaseModel):
    """
    AI 聊天记录模型
    
    用于存储 AI 回复的请求和响应记录，包括状态、耗时、错误信息等。
    继承自 BaseModel，自动包含 id、created_at、updated_at 字段。
    """
    
    __tablename__ = "ai_chat_records"
    
    # 记录唯一标识（使用 ID 生成器生成）
    record_id = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="记录唯一标识",
    )
    
    # 会话ID
    session_id = Column(
        String(48),
        nullable=False,
        index=True,
        comment="会话ID",
    )
    
    # 用户消息ID（关联 messages 表的 message_id）
    user_message_id = Column(
        String(64),
        nullable=False,
        index=True,
        comment="用户消息ID",
    )
    
    # AI回复消息ID（关联 messages 表的 message_id，可选）
    ai_message_id = Column(
        String(64),
        nullable=True,
        index=True,
        comment="AI回复消息ID",
    )
    
    # 请求内容（JSON格式）
    request_content = Column(
        Text,
        nullable=True,
        comment="请求内容（JSON格式）",
    )
    
    # 响应内容（JSON格式）
    response_content = Column(
        Text,
        nullable=True,
        comment="响应内容（JSON格式）",
    )
    
    # 状态：0-处理中，1-成功，2-失败
    status = Column(
        Integer,
        nullable=False,
        default=0,
        index=True,
        comment="状态：0-处理中，1-成功，2-失败",
    )
    
    # 处理耗时（毫秒）
    duration_ms = Column(
        BigInteger,
        nullable=True,
        comment="处理耗时（毫秒）",
    )
    
    # 错误信息
    error_message = Column(
        String(500),
        nullable=True,
        comment="错误信息",
    )
    
    # 添加复合索引以提高查询性能
    __table_args__ = (
        Index("idx_session_status", "session_id", "status"),
        Index("idx_session_created", "session_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        return f"<AIChatRecord(id={self.id}, record_id='{self.record_id}', session_id='{self.session_id}', status={self.status})>"

