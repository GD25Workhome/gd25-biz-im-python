"""
Repository 模块

提供数据访问层（Repository Pattern）的实现。
"""

from app.repositories.base import (
    BaseRepository,
    PaginationParams,
    PaginationResult,
    ModelType,
)

__all__ = [
    "BaseRepository",
    "PaginationParams",
    "PaginationResult",
    "ModelType",
]

