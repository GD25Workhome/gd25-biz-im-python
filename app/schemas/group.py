"""
群组 Schema

使用 Pydantic 定义群组相关的数据验证和序列化模式。
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class GroupCreate(BaseModel):
    """
    群组创建 Schema
    
    用于创建新群组的请求数据验证。
    """
    
    group_name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="群组名称"
    )
    
    description: Optional[str] = Field(
        None,
        description="群组描述"
    )


class GroupResponse(BaseModel):
    """
    群组响应 Schema
    
    用于返回群组信息的响应数据。
    """
    
    id: int = Field(..., description="主键ID")
    group_id: str = Field(..., description="群组唯一标识")
    group_name: str = Field(..., description="群组名称")
    description: Optional[str] = Field(None, description="群组描述")
    created_by: str = Field(..., description="创建人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 模型创建


class GroupMemberAdd(BaseModel):
    """
    群组成员添加 Schema
    
    用于添加群组成员的请求数据验证。
    """
    
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=48,
        description="用户ID"
    )
    
    user_role: Literal['PATIENT', 'DOCTOR', 'AI_ASSISTANT'] = Field(
        ...,
        description="用户在群组中的身份标签：PATIENT/DOCTOR/AI_ASSISTANT"
    )
