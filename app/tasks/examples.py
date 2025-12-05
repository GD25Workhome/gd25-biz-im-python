"""
Celery 任务示例模块

提供任务定义示例，展示如何使用 Celery 任务。
"""

import time
import logging
from typing import Dict, Any
from app.tasks.base import task, BaseTask
from app.tasks.celery_app import celery_app

# 配置日志
logger = logging.getLogger(__name__)


# ==================== 示例 1：简单任务 ====================

@celery_app.task(name="app.tasks.examples.simple_task")
def simple_task(message: str) -> str:
    """
    简单任务示例
    
    这是一个最简单的任务定义，直接使用 celery_app.task 装饰器。
    
    Args:
        message: 消息内容
    
    Returns:
        str: 处理后的消息
    """
    logger.info(f"处理消息: {message}")
    return f"处理完成: {message}"


# ==================== 示例 2：使用任务装饰器 ====================

@task(name="app.tasks.examples.decorated_task")
def decorated_task(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用自定义装饰器的任务示例
    
    使用 @task 装饰器可以简化任务定义，自动应用 BaseTask 的功能。
    
    Args:
        data: 任务数据
    
    Returns:
        Dict[str, Any]: 处理结果
    """
    logger.info(f"处理数据: {data}")
    return {
        "status": "success",
        "data": data,
        "processed_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }


# ==================== 示例 3：可重试任务 ====================

@task(name="app.tasks.examples.retryable_task", bind=True, max_retries=3, default_retry_delay=10)
def retryable_task(self, value: int) -> int:
    """
    可重试任务示例
    
    使用 bind=True 可以访问任务实例（self），从而可以调用 self.retry() 进行重试。
    
    Args:
        self: 任务实例（bind=True 时可用）
        value: 输入值
    
    Returns:
        int: 处理结果
    
    Raises:
        Exception: 当处理失败时抛出异常，触发重试
    """
    logger.info(f"处理值: {value}")
    
    # 模拟可能失败的操作
    if value < 0:
        # 重试任务
        logger.warning(f"值 {value} 无效，将在 {self.default_retry_delay} 秒后重试")
        raise self.retry(exc=ValueError(f"值 {value} 无效"), countdown=self.default_retry_delay)
    
    return value * 2


# ==================== 示例 4：长时间运行的任务 ====================

@task(name="app.tasks.examples.long_running_task")
def long_running_task(duration: int = 5) -> str:
    """
    长时间运行的任务示例
    
    模拟需要较长时间处理的任务。
    
    Args:
        duration: 任务持续时间（秒）
    
    Returns:
        str: 完成消息
    """
    logger.info(f"开始长时间任务，预计耗时 {duration} 秒")
    
    for i in range(duration):
        time.sleep(1)
        logger.info(f"任务进度: {i + 1}/{duration}")
    
    logger.info("长时间任务完成")
    return f"任务完成，耗时 {duration} 秒"


# ==================== 示例 5：链式任务 ====================

@task(name="app.tasks.examples.chain_task_1")
def chain_task_1(data: str) -> str:
    """链式任务第一步"""
    logger.info(f"链式任务 1: 处理 {data}")
    return f"步骤1完成: {data}"


@task(name="app.tasks.examples.chain_task_2")
def chain_task_2(data: str) -> str:
    """链式任务第二步"""
    logger.info(f"链式任务 2: 处理 {data}")
    return f"步骤2完成: {data}"


@task(name="app.tasks.examples.chain_task_3")
def chain_task_3(data: str) -> str:
    """链式任务第三步"""
    logger.info(f"链式任务 3: 处理 {data}")
    return f"步骤3完成: {data}"


# ==================== 使用示例 ====================
# 
# 在代码中使用这些任务：
#
# from app.tasks.examples import (
#     simple_task,
#     decorated_task,
#     retryable_task,
#     long_running_task,
#     chain_task_1,
#     chain_task_2,
#     chain_task_3,
# )
# from celery import chain
#
# # 1. 简单任务
# result = simple_task.delay("Hello, World!")
# print(result.get())  # 等待结果
#
# # 2. 异步任务（不等待结果）
# decorated_task.delay({"key": "value"})
#
# # 3. 可重试任务
# result = retryable_task.delay(10)
# print(result.get())
#
# # 4. 长时间任务
# result = long_running_task.delay(10)
# print(result.get())
#
# # 5. 链式任务
# workflow = chain(
#     chain_task_1.s("初始数据"),
#     chain_task_2.s(),
#     chain_task_3.s()
# )
# result = workflow.apply_async()
# print(result.get())


# ==================== 导出 ====================
__all__ = [
    "simple_task",
    "decorated_task",
    "retryable_task",
    "long_running_task",
    "chain_task_1",
    "chain_task_2",
    "chain_task_3",
]

