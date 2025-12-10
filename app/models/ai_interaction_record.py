"""
AI交互记录模型

定义 AI 交互记录表的数据模型，用于存储 AI 服务调用情况。
"""

from sqlalchemy import Column, String, Text, Integer, BigInteger, Index
from app.db.base import BaseModel


class AIInteractionRecord(BaseModel):
    """
    AI交互记录模型
    
    用于存储 AI 服务调用的请求和响应记录，包括状态、耗时、错误信息等。
    继承自 BaseModel，自动包含 id、created_at、updated_at 字段。
    
    示例：
        ```python
        from app.models.ai_interaction_record import AIInteractionRecord
        from app.db.session import get_db_session
        
        db = get_db_session()
        record = AIInteractionRecord(
            record_id="record_001",
            group_id="group_001",
            user_message_id="msg_001",
            ai_message_id="msg_002",
            ai_service_url="https://ai.example.com/api",
            status=1,
            duration_ms=500
        )
        db.add(record)
        db.commit()
        ```
    """
    
    __tablename__ = "ai_interaction_records"
    
    # 记录唯一标识（使用 ID 生成器生成）
    record_id = Column(
        String(64),
        unique=True,
        nullable=False,
        comment="记录唯一标识",
    )
    
    # 群组ID
    group_id = Column(
        String(64),
        nullable=False,
        comment="群组ID",
    )
    
    # 用户消息ID（关联 messages 表的 message_id）
    user_message_id = Column(
        String(64),
        nullable=False,
        comment="用户消息ID",
    )
    
    # AI回复消息ID（关联 messages 表的 message_id，可选）
    ai_message_id = Column(
        String(64),
        nullable=True,
        comment="AI回复消息ID",
    )
    
    # AI服务URL
    ai_service_url = Column(
        String(256),
        nullable=True,
        comment="AI服务URL",
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
    
    # 添加索引以提高查询性能
    __table_args__ = (
        Index("idx_group_id", "group_id"),
        Index("idx_user_message_id", "user_message_id"),
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        return f"<AIInteractionRecord(id={self.id}, record_id='{self.record_id}', group_id='{self.group_id}', status={self.status})>"
