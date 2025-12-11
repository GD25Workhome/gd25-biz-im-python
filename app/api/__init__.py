"""
API 路由模块

导出所有路由，方便统一导入和注册。
"""

from app.api import user, group, message

__all__ = ["user", "group", "message"]

