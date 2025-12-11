"""
Schema 模块

导出所有 Schema，方便统一导入。
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)

from app.schemas.group import (
    GroupCreate,
    GroupResponse,
    GroupMemberAdd,
)

from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
)

__all__ = [
    # 用户 Schema
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # 群组 Schema
    "GroupCreate",
    "GroupResponse",
    "GroupMemberAdd",
    # 消息 Schema
    "MessageCreate",
    "MessageResponse",
    "MessageListResponse",
]
