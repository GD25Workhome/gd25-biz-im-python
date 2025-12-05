"""
Celery 任务模块

提供 Celery 异步任务队列的基础配置和任务定义。
"""

from app.tasks.celery_app import celery_app, make_celery_app
from app.tasks.base import BaseTask, task

__all__ = [
    "celery_app",
    "make_celery_app",
    "BaseTask",
    "task",
]

