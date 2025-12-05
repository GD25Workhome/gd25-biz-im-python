"""
用户 Schema 示例

使用 Pydantic 定义用户相关的数据验证和序列化模式。
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ==================== 基础 Schema ====================

class UserBase(BaseModel):
    """用户基础 Schema"""
    
    name: str = Field(..., min_length=1, max_length=100, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    is_active: bool = Field(default=True, description="是否激活")


# ==================== 创建 Schema ====================

class UserCreate(UserBase):
    """创建用户 Schema"""
    
    pass


# ==================== 更新 Schema ====================

class UserUpdate(BaseModel):
    """更新用户 Schema"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    is_active: Optional[bool] = Field(None, description="是否激活")


# ==================== 响应 Schema ====================

class UserResponse(UserBase):
    """用户响应 Schema"""
    
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    
    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 模型创建


# ==================== 列表响应 Schema ====================

class UserListResponse(BaseModel):
    """用户列表响应 Schema"""
    
    items: list[UserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

