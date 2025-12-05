"""
用户 API 路由示例

展示如何创建 FastAPI 路由，集成 Service 层和 Schema。
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.user_service import UserService
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)
from app.repositories.base import PaginationResult
from app.models.user import User
from app.utils.response import success_response

# 创建路由器
router = APIRouter(prefix="/users", tags=["用户"])


# ==================== 依赖注入 ====================

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    获取用户服务实例（依赖注入）
    
    Args:
        db: 数据库会话
        
    Returns:
        UserService: 用户服务实例
    """
    return UserService(db)


# ==================== API 路由 ====================

@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建一个新用户",
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    创建用户
    
    Args:
        user_data: 用户创建数据
        service: 用户服务（依赖注入）
        
    Returns:
        dict: 创建的用户信息
    """
    user = service.create_user(user_data)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="用户创建成功"
    )


@router.get(
    "/{user_id}",
    response_model=dict,
    summary="获取用户",
    description="根据 ID 获取用户信息",
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    获取用户
    
    Args:
        user_id: 用户ID
        service: 用户服务（依赖注入）
        
    Returns:
        dict: 用户信息
    """
    user = service.get_user_by_id(user_id)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="获取用户成功"
    )


@router.put(
    "/{user_id}",
    response_model=dict,
    summary="更新用户",
    description="更新用户信息",
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    更新用户
    
    Args:
        user_id: 用户ID
        user_data: 用户更新数据
        service: 用户服务（依赖注入）
        
    Returns:
        dict: 更新后的用户信息
    """
    user = service.update_user(user_id, user_data)
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="用户更新成功"
    )


@router.delete(
    "/{user_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="删除用户",
    description="删除用户",
)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    删除用户
    
    Args:
        user_id: 用户ID
        service: 用户服务（依赖注入）
        
    Returns:
        dict: 删除结果
    """
    service.delete_user(user_id)
    return success_response(message="用户删除成功")


@router.get(
    "/",
    response_model=dict,
    summary="获取用户列表",
    description="分页获取用户列表",
)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否激活（可选）"),
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    获取用户列表
    
    Args:
        page: 页码
        page_size: 每页数量
        is_active: 是否激活（可选）
        service: 用户服务（依赖注入）
        
    Returns:
        dict: 用户列表（分页）
    """
    result: PaginationResult[User] = service.get_users(
        page=page,
        page_size=page_size,
        is_active=is_active
    )
    
    # 转换为响应格式
    items = [UserResponse.model_validate(user).model_dump() for user in result.items]
    
    return success_response(
        data={
            "items": items,
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev,
        },
        message="获取用户列表成功"
    )


@router.get(
    "/search",
    response_model=dict,
    summary="搜索用户",
    description="根据关键词搜索用户",
)
async def search_users(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    搜索用户
    
    Args:
        keyword: 搜索关键词
        page: 页码
        page_size: 每页数量
        service: 用户服务（依赖注入）
        
    Returns:
        dict: 搜索结果（分页）
    """
    result: PaginationResult[User] = service.search_users(
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    
    # 转换为响应格式
    items = [UserResponse.model_validate(user).model_dump() for user in result.items]
    
    return success_response(
        data={
            "items": items,
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev,
        },
        message="搜索用户成功"
    )

