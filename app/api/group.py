"""
群组 API 路由

提供群组相关的HTTP API接口。
"""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.core.group_service import GroupService
from app.schemas.group import GroupCreate, GroupResponse, GroupMemberAdd
from app.utils.response import success_response
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError


# 创建路由器
router = APIRouter(tags=["群组"])


# ==================== 依赖注入 ====================

def get_group_service(db: Session = Depends(get_db)) -> GroupService:
    """
    获取群组服务实例（依赖注入）
    
    Args:
        db: 数据库会话
        
    Returns:
        GroupService: 群组服务实例
    """
    return GroupService(db)


# ==================== API 路由 ====================

@router.post(
    "/group/create",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="创建群组",
    description="创建一个新群组，创建人会自动添加为成员（身份为DOCTOR）",
)
async def create_group(
    group_create: GroupCreate,
    creator_id: str = Query(..., description="创建人ID"),
    service: GroupService = Depends(get_group_service),
) -> dict:
    """
    创建群组
    
    创建群组时，会自动将创建人添加为群组成员，身份为DOCTOR。
    
    Args:
        group_create: 群组创建数据
        creator_id: 创建人ID（查询参数）
        service: 群组服务（依赖注入）
        
    Returns:
        dict: 创建的群组信息
        
    Raises:
        HTTPException: 当创建失败时抛出
    """
    try:
        group_response = service.create_group(group_create, creator_id)
        return success_response(
            data=group_response.model_dump(),
            message="群组创建成功"
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
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建群组失败: {str(e)}"
        )


@router.get(
    "/group/{group_id}",
    response_model=dict,
    summary="获取群组信息",
    description="根据 group_id 获取群组信息",
)
async def get_group(
    group_id: str,
    service: GroupService = Depends(get_group_service),
) -> dict:
    """
    获取群组信息
    
    Args:
        group_id: 群组唯一标识
        service: 群组服务（依赖注入）
        
    Returns:
        dict: 群组信息
        
    Raises:
        HTTPException: 当群组不存在时抛出
    """
    group_response = service.get_group(group_id)
    if not group_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"群组 {group_id} 不存在"
        )
    
    return success_response(
        data=group_response.model_dump(),
        message="获取群组成功"
    )


@router.post(
    "/group/{group_id}/members",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="添加群组成员",
    description="向群组添加新成员",
)
async def add_member(
    group_id: str,
    member_add: GroupMemberAdd,
    service: GroupService = Depends(get_group_service),
) -> dict:
    """
    添加群组成员
    
    Args:
        group_id: 群组ID
        member_add: 成员添加数据
        service: 群组服务（依赖注入）
        
    Returns:
        dict: 添加结果
        
    Raises:
        HTTPException: 当添加失败时抛出
    """
    try:
        success = service.add_member(group_id, member_add)
        return success_response(
            data={"success": success},
            message="添加成员成功"
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
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加成员失败: {str(e)}"
        )


@router.get(
    "/group/{group_id}/members",
    response_model=dict,
    summary="获取群组成员列表",
    description="获取群组的所有成员列表",
)
async def get_group_members(
    group_id: str,
    service: GroupService = Depends(get_group_service),
) -> dict:
    """
    获取群组成员列表
    
    Args:
        group_id: 群组ID
        service: 群组服务（依赖注入）
        
    Returns:
        dict: 成员列表
        
    Raises:
        HTTPException: 当群组不存在时抛出
    """
    try:
        members = service.get_group_members(group_id)
        return success_response(
            data={"members": members},
            message="获取成员列表成功"
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取成员列表失败: {str(e)}"
        )
