"""
用户 API 路由

提供用户相关的HTTP API接口。
"""

from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db
from app.services.core.user_service import UserService
from app.schemas.user import UserCreate, UserResponse
from app.utils.response import success_response
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError


# 创建路由器
router = APIRouter(tags=["用户"])


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


# ==================== 请求/响应模型 ====================

class UpdateUserRoleRequest(BaseModel):
    """更新用户身份请求"""
    user_role: str


# ==================== API 路由 ====================

@router.post(
    "/user/create",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建一个新用户",
)
async def create_user(
    user_create: UserCreate,
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    创建用户
    
    Args:
        user_create: 用户创建数据
        service: 用户服务（依赖注入）
        
    Returns:
        dict: 创建的用户信息
        
    Raises:
        HTTPException: 当创建失败时抛出
    """
    try:
        user_response = service.create_user(user_create)
        return success_response(
            data=user_response.model_dump(),
            message="用户创建成功"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )


@router.get(
    "/user/{user_id}",
    response_model=dict,
    summary="获取用户信息",
    description="根据 user_id 获取用户信息",
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    获取用户信息
    
    Args:
        user_id: 用户唯一标识
        service: 用户服务（依赖注入）
        
    Returns:
        dict: 用户信息
        
    Raises:
        HTTPException: 当用户不存在时抛出
    """
    user_response = service.get_user(user_id)
    if not user_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在"
        )
    
    return success_response(
        data=user_response.model_dump(),
        message="获取用户成功"
    )


@router.put(
    "/user/{user_id}/role",
    response_model=dict,
    summary="更新用户身份标签",
    description="更新用户的身份标签（PATIENT/DOCTOR/AI_ASSISTANT）",
)
async def update_user_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    更新用户身份标签
    
    Args:
        user_id: 用户唯一标识
        request: 更新请求（包含新的user_role）
        service: 用户服务（依赖注入）
        
    Returns:
        dict: 更新后的用户信息
        
    Raises:
        HTTPException: 当用户不存在或user_role无效时抛出
    """
    try:
        user_response = service.update_user_role(user_id, request.user_role)
        return success_response(
            data=user_response.model_dump(),
            message="用户身份更新成功"
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户身份失败: {str(e)}"
        )
