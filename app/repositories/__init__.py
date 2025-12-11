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

from app.repositories.user_repository import UserRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.group_member_repository import GroupMemberRepository
from app.repositories.message_repository import MessageRepository

__all__ = [
    # 基础类
    "BaseRepository",
    "PaginationParams",
    "PaginationResult",
    "ModelType",
    # 业务 Repository
    "UserRepository",
    "GroupRepository",
    "GroupMemberRepository",
    "MessageRepository",
]
