"""
用户 Schema

使用 Pydantic 定义用户相关的数据验证和序列化模式。
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    """
    用户创建 Schema
    
    用于创建新用户的请求数据验证。
    """
    
    username: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="用户名"
    )
    
    user_role: Literal['PATIENT', 'DOCTOR', 'AI_ASSISTANT'] = Field(
        default='PATIENT',
        description="用户身份：PATIENT(患者)/DOCTOR(医生)/AI_ASSISTANT(医生AI助手)"
    )


class UserUpdate(BaseModel):
    """
    用户更新 Schema
    
    用于更新用户信息的请求数据验证。
    """
    
    username: Optional[str] = Field(
        None,
        min_length=1,
        max_length=64,
        description="用户名"
    )
    
    user_role: Optional[Literal['PATIENT', 'DOCTOR', 'AI_ASSISTANT']] = Field(
        None,
        description="用户身份：PATIENT(患者)/DOCTOR(医生)/AI_ASSISTANT(医生AI助手)"
    )


class UserResponse(BaseModel):
    """
    用户响应 Schema
    
    用于返回用户信息的响应数据。
    """
    
    id: int = Field(..., description="主键ID")
    user_id: str = Field(..., description="用户唯一标识")
    username: str = Field(..., description="用户名")
    user_role: str = Field(..., description="用户身份")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 模型创建
