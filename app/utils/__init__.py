"""
工具类模块

提供日志、ID 生成、响应格式、异常处理等通用工具。
"""

from app.utils.logger import logger, get_logger, setup_logger
from app.utils.id_generator import generate_id, generate_short_id, generate_numeric_id
from app.utils.response import (
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    success_response,
    error_response,
)
from app.utils.exceptions import (
    BaseAppException,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    InternalServerError,
)

__all__ = [
    # 日志工具
    "logger",
    "get_logger",
    "setup_logger",
    # ID 生成器
    "generate_id",
    "generate_short_id",
    "generate_numeric_id",
    # 响应格式
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "success_response",
    "error_response",
    # 异常类
    "BaseAppException",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "InternalServerError",
]

