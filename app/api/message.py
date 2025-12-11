"""
消息 API 路由

提供消息相关的HTTP API接口。
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.core.message_service import MessageService
from app.schemas.message import MessageCreate, MessageResponse, MessageListResponse
from app.utils.response import success_response
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError


# 创建路由器
router = APIRouter(tags=["消息"])


# ==================== 依赖注入 ====================

def get_message_service(db: Session = Depends(get_db)) -> MessageService:
    """
    获取消息服务实例（依赖注入）
    
    Args:
        db: 数据库会话
        
    Returns:
        MessageService: 消息服务实例
    """
    return MessageService(db)


# ==================== API 路由 ====================

@router.post(
    "/message/send",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="发送消息",
    description="在群组中发送消息。发送人必须是群组成员。",
)
async def send_message(
    message_create: MessageCreate,
    from_user_id: str = Query(..., description="发送人ID"),
    service: MessageService = Depends(get_message_service),
) -> dict:
    """
    发送消息
    
    在群组中发送消息。发送人必须是群组成员。
    
    Args:
        message_create: 消息创建数据（包含group_id和content）
        from_user_id: 发送人ID（查询参数）
        service: 消息服务（依赖注入）
        
    Returns:
        dict: 创建的消息信息
        
    Raises:
        HTTPException: 当发送失败时抛出
    """
    try:
        message_response = service.send_message(message_create, from_user_id)
        return success_response(
            data=message_response.model_dump(),
            message="消息发送成功"
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
            detail=f"发送消息失败: {str(e)}"
        )


@router.get(
    "/message/{message_id}",
    response_model=dict,
    summary="获取单条消息",
    description="根据 message_id 获取单条消息详情",
)
async def get_message(
    message_id: str,
    service: MessageService = Depends(get_message_service),
) -> dict:
    """
    获取单条消息
    
    Args:
        message_id: 消息唯一标识
        service: 消息服务（依赖注入）
        
    Returns:
        dict: 消息信息
        
    Raises:
        HTTPException: 当消息不存在时抛出
    """
    try:
        message_response = service.get_message(message_id)
        return success_response(
            data=message_response.model_dump(),
            message="获取消息成功"
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取消息失败: {str(e)}"
        )


@router.get(
    "/message/list",
    response_model=dict,
    summary="获取消息列表",
    description="获取群组的消息列表，支持分页",
)
async def get_messages(
    group_id: str = Query(..., description="群组ID"),
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量（1-100）"),
    service: MessageService = Depends(get_message_service),
) -> dict:
    """
    获取消息列表
    
    获取群组的消息列表，支持分页。消息按创建时间倒序排列。
    
    Args:
        group_id: 群组ID（查询参数）
        page: 页码（从1开始，默认1）
        page_size: 每页数量（1-100，默认20）
        service: 消息服务（依赖注入）
        
    Returns:
        dict: 消息列表和分页信息
        
    Raises:
        HTTPException: 当获取失败时抛出
    """
    try:
        messages, total = service.get_messages(group_id, page, page_size)
        
        # 转换为字典列表
        messages_data = [msg.model_dump() for msg in messages]
        
        return success_response(
            data={
                "messages": messages_data,
                "total": total,
                "page": page,
                "page_size": page_size
            },
            message="获取消息列表成功"
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
            detail=f"获取消息列表失败: {str(e)}"
        )
