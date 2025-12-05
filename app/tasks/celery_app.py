"""
Celery 应用配置模块

提供 Celery 异步任务队列的基础配置，支持 RabbitMQ 作为 Broker。
包含任务序列化、超时设置、Worker 参数等配置。
"""

import logging
from typing import Optional, Any, Dict
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from app.config import settings

# 配置日志
logger = logging.getLogger(__name__)


def make_celery_app() -> Celery:
    """
    创建并配置 Celery 应用实例
    
    根据配置创建 Celery 应用，支持 RabbitMQ 或 Redis 作为 Broker。
    必须通过环境变量 CELERY_BROKER_URL 配置 Broker URL，不允许使用硬编码的凭证。
    
    Returns:
        Celery: 配置好的 Celery 应用实例
    
    Raises:
        ValueError: 当 CELERY_BROKER_URL 未配置时抛出
    """
    # 获取 Broker URL，必须通过环境变量配置
    broker_url = settings.celery_broker_url
    if not broker_url:
        error_msg = (
            "CELERY_BROKER_URL 未配置。请设置环境变量 CELERY_BROKER_URL 或在 .env 文件中配置。\n"
            "示例：CELERY_BROKER_URL=amqp://user:password@localhost:5672/\n"
            "或使用 Redis：CELERY_BROKER_URL=redis://localhost:6379/0\n"
            "注意：为了安全，不允许在代码中使用硬编码的凭证。"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # 获取 Result Backend URL（可选）
    result_backend = settings.celery_result_backend
    if not result_backend:
        # 如果不配置 Result Backend，任务可以执行但无法获取结果
        logger.info(
            "CELERY_RESULT_BACKEND 未配置，任务将无法返回结果（fire-and-forget 模式）"
        )
    
    # 创建 Celery 应用
    celery_app = Celery(
        "gd25-arch-backend",
        broker=broker_url,
        backend=result_backend,
    )
    
    # ==================== 任务序列化配置 ====================
    # 使用 JSON 序列化（安全、跨语言兼容）
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],  # 只接受 JSON 格式的消息
        result_serializer="json",
        timezone="Asia/Shanghai",  # 时区设置
        enable_utc=True,  # 启用 UTC 时间
    )
    
    # ==================== 任务超时设置 ====================
    celery_app.conf.update(
        task_soft_time_limit=300,  # 软超时：300 秒（5 分钟）
        task_time_limit=600,  # 硬超时：600 秒（10 分钟）
        task_acks_late=True,  # 任务完成后才确认（提高可靠性）
        task_reject_on_worker_lost=True,  # Worker 丢失时拒绝任务
    )
    
    # ==================== Worker 参数配置 ====================
    celery_app.conf.update(
        worker_prefetch_multiplier=4,  # Worker 预取任务数量（提高吞吐量）
        worker_max_tasks_per_child=1000,  # 每个子进程最多处理的任务数（防止内存泄漏）
        worker_disable_rate_limits=False,  # 启用速率限制
    )
    
    # ==================== 结果后端配置 ====================
    if result_backend:
        celery_app.conf.update(
            result_expires=3600,  # 结果过期时间：1 小时
            result_backend_transport_options={
                "master_name": "mymaster",  # Redis Sentinel 配置（如果使用）
            },
        )
    
    # ==================== 路由配置（可选）====================
    # 可以根据任务名称路由到不同的队列
    celery_app.conf.task_routes = {
        # 示例：高优先级任务路由到 high_priority 队列
        # "app.tasks.high_priority.*": {"queue": "high_priority"},
        # 示例：低优先级任务路由到 low_priority 队列
        # "app.tasks.low_priority.*": {"queue": "low_priority"},
    }
    
    # ==================== 任务发现配置 ====================
    # 自动发现任务模块
    celery_app.conf.imports = (
        "app.tasks",  # 自动导入 app.tasks 模块下的所有任务
    )
    
    # ==================== 信号处理 ====================
    # 任务执行前
    @task_prerun.connect
    def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
        """任务执行前的处理"""
        logger.info(
            f"任务开始执行: {task.name} (ID: {task_id})"
        )
    
    # 任务执行后
    @task_postrun.connect
    def task_postrun_handler(
        sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds
    ):
        """任务执行后的处理"""
        logger.info(
            f"任务执行完成: {task.name} (ID: {task_id}, State: {state})"
        )
    
    # 任务失败
    @task_failure.connect
    def task_failure_handler(
        sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds
    ):
        """任务失败时的处理"""
        logger.error(
            f"任务执行失败: {sender.name} (ID: {task_id}, Exception: {exception})"
        )
    
    logger.info(f"Celery 应用初始化完成 - Broker: {broker_url}")
    if result_backend:
        logger.info(f"Result Backend: {result_backend}")
    
    return celery_app


# 创建全局 Celery 应用实例
celery_app = make_celery_app()


# ==================== 导出 ====================
__all__ = ["celery_app", "make_celery_app"]
