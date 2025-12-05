"""
统一响应格式模块

提供 FastAPI 统一响应格式，便于前端处理。
"""

from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """
    基础响应模型
    
    所有 API 响应都应使用此格式。
    """
    
    code: int = Field(
        default=200,
        description="响应状态码，200 表示成功",
    )
    message: str = Field(
        default="success",
        description="响应消息",
    )
    data: Optional[T] = Field(
        default=None,
        description="响应数据",
    )
    timestamp: str = Field(
        default_factory=lambda: __import__("datetime").datetime.now().isoformat(),
        description="响应时间戳",
    )


class SuccessResponse(BaseResponse[T]):
    """
    成功响应模型
    
    用于返回成功的结果。
    """
    
    code: int = Field(default=200, description="状态码：200")
    message: str = Field(default="success", description="成功消息")


class ErrorResponse(BaseResponse[None]):
    """
    错误响应模型
    
    用于返回错误信息。
    """
    
    code: int = Field(default=400, description="错误状态码")
    message: str = Field(default="error", description="错误消息")
    data: None = Field(default=None, description="错误响应不包含数据")


def success_response(
    data: Optional[T] = None,
    message: str = "success",
    code: int = 200,
) -> Dict[str, Any]:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码
        
    Returns:
        dict: 成功响应字典
        
    Example:
        ```python
        from app.utils.response import success_response
        
        return success_response(data={"user_id": 123}, message="用户创建成功")
        ```
    """
    from datetime import datetime
    
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }


def error_response(
    message: str = "error",
    code: int = 400,
    data: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    创建错误响应
    
    Args:
        message: 错误消息
        code: 错误状态码
        data: 可选的错误详情
        
    Returns:
        dict: 错误响应字典
        
    Example:
        ```python
        from app.utils.response import error_response
        
        return error_response(message="用户不存在", code=404)
        ```
    """
    from datetime import datetime
    
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }


__all__ = [
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "success_response",
    "error_response",
]

