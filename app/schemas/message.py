"""
消息 Schema

使用 Pydantic 定义消息相关的数据验证和序列化模式。
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class MessageCreate(BaseModel):
    """
    消息创建 Schema
    
    用于创建新消息的请求数据验证。
    """
    
    group_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="群组ID"
    )
    
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="消息内容"
    )


class MessageResponse(BaseModel):
    """
    消息响应 Schema
    
    用于返回消息信息的响应数据。
    """
    
    id: int = Field(..., description="主键ID")
    message_id: str = Field(..., description="消息唯一标识")
    group_id: str = Field(..., description="群组ID")
    from_user_id: str = Field(..., description="发送人ID")
    msg_type: str = Field(..., description="消息类型：TEXT/IMAGE/AI_REPLY")
    msg_content: str = Field(..., description="消息内容")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 模型创建


class MessageListResponse(BaseModel):
    """
    消息列表响应 Schema
    
    用于返回消息列表的响应数据，包含分页信息。
    """
    
    messages: List[MessageResponse] = Field(..., description="消息列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
