"""
API 路由模块

导出所有路由，方便统一导入和注册。
"""

from app.api.users import router as users_router

__all__ = ["users_router"]

