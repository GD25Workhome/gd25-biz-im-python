"""
Celery 任务基础类模块

提供基础任务类和装饰器，简化任务定义和使用。
"""

import logging
from typing import Any, Callable, Optional, Dict
from functools import wraps
from celery import Task
from app.tasks.celery_app import celery_app

# 配置日志
logger = logging.getLogger(__name__)


class BaseTask(Task):
    """
    基础任务类
    
    提供通用的任务功能，包括：
    - 自动日志记录
    - 错误处理
    - 任务状态跟踪
    """
    
    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
        """
        任务成功完成时的回调
        
        Args:
            retval: 任务返回值
            task_id: 任务 ID
            args: 任务参数
            kwargs: 任务关键字参数
        """
        logger.info(
            f"任务成功完成: {self.name} (ID: {task_id})"
        )
    
    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """
        任务失败时的回调
        
        Args:
            exc: 异常对象
            task_id: 任务 ID
            args: 任务参数
            kwargs: 任务关键字参数
            einfo: 异常信息
        """
        logger.error(
            f"任务执行失败: {self.name} (ID: {task_id}, Exception: {exc})",
            exc_info=True
        )
    
    def on_retry(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """
        任务重试时的回调
        
        Args:
            exc: 异常对象
            task_id: 任务 ID
            args: 任务参数
            kwargs: 任务关键字参数
            einfo: 异常信息
        """
        logger.warning(
            f"任务重试: {self.name} (ID: {task_id}, Exception: {exc})"
        )


def task(
    name: Optional[str] = None,
    bind: bool = False,
    base: type = BaseTask,
    max_retries: int = 3,
    default_retry_delay: int = 60,
    **kwargs
) -> Callable:
    """
    任务装饰器
    
    简化任务定义，提供统一的配置和错误处理。
    
    Args:
        name: 任务名称（可选，默认使用函数名）
        bind: 是否绑定任务实例（允许访问 self）
        base: 基础任务类（默认使用 BaseTask）
        max_retries: 最大重试次数
        default_retry_delay: 默认重试延迟（秒）
        **kwargs: 其他 Celery 任务参数
    
    Returns:
        Callable: 装饰后的任务函数
    
    Examples:
        ```python
        @task(name="send_email")
        def send_email_task(email: str, subject: str):
            # 任务逻辑
            pass
        
        @task(bind=True, max_retries=5)
        def retryable_task(self, data: dict):
            try:
                # 任务逻辑
                pass
            except Exception as exc:
                # 重试任务
                raise self.retry(exc=exc, countdown=60)
        ```
    """
    def decorator(func: Callable) -> Callable:
        # 使用 celery_app.task 装饰器
        task_func = celery_app.task(
            name=name or f"app.tasks.{func.__name__}",
            bind=bind,
            base=base,
            max_retries=max_retries,
            default_retry_delay=default_retry_delay,
            **kwargs
        )(func)
        
        return task_func
    
    return decorator


# ==================== 导出 ====================
__all__ = ["BaseTask", "task"]

