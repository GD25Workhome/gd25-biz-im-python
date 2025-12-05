"""
主应用入口模块

提供 FastAPI 应用的基础配置和入口文件，包括：
- 应用初始化
- 中间件配置（CORS、异常处理、请求日志）
- 基础路由（健康检查、版本信息）
- 生命周期事件（启动、关闭）
- API 文档配置
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.db.database import get_engine, close_engine, check_connection
from app.utils.exceptions import BaseAppException
from app.utils.response import success_response


# 配置日志
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    管理应用的启动和关闭事件，包括数据库连接初始化。
    
    Args:
        app: FastAPI 应用实例
    """
    # 启动事件
    logger.info("应用启动中...")
    
    # 验证数据库配置
    try:
        settings.validate_database_config()
        logger.info("数据库配置验证通过")
    except ValueError as e:
        logger.error(f"数据库配置验证失败: {e}")
        raise
    
    # 初始化数据库连接
    try:
        engine = get_engine()
        logger.info("数据库引擎初始化成功")
        
        # 测试数据库连接
        if check_connection():
            logger.info("数据库连接测试成功")
        else:
            logger.warning("数据库连接测试失败，但应用将继续启动")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        # 在开发环境中，允许数据库未配置时继续启动
        if settings.is_production():
            raise
    
    logger.info(f"应用启动完成 - {settings.app_name} v{settings.app_version}")
    
    yield
    
    # 关闭事件
    logger.info("应用关闭中...")
    
    # 关闭数据库连接
    try:
        close_engine()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接时出错: {e}")
    
    logger.info("应用已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI 后端脚手架 - 通用的项目基础框架",
    docs_url="/docs" if not settings.is_production() else None,  # 生产环境禁用文档
    redoc_url="/redoc" if not settings.is_production() else None,  # 生产环境禁用文档
    openapi_url="/openapi.json" if not settings.is_production() else None,  # 生产环境禁用 OpenAPI
    lifespan=lifespan,
)


# ==================== 中间件配置 ====================

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件（可选）
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求日志中间件
    
    记录每个请求的基本信息，包括请求路径、方法、处理时间等。
    """
    start_time = time.time()
    
    # 记录请求信息
    logger.info(
        f"请求: {request.method} {request.url.path} - "
        f"客户端: {request.client.host if request.client else 'unknown'}"
    )
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应信息
    logger.info(
        f"响应: {request.method} {request.url.path} - "
        f"状态码: {response.status_code} - "
        f"处理时间: {process_time:.3f}s"
    )
    
    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# ==================== 异常处理 ====================

@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    """
    应用自定义异常处理器
    
    处理所有继承自 BaseAppException 的自定义异常。
    """
    logger.error(
        f"应用异常: {exc.message} (代码: {exc.code}) - "
        f"路径: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTP 异常处理器
    
    处理 FastAPI 和 Starlette 的 HTTP 异常。
    """
    logger.warning(
        f"HTTP 异常: {exc.status_code} - {exc.detail} - "
        f"路径: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求验证异常处理器
    
    处理 Pydantic 验证错误。
    """
    logger.warning(
        f"请求验证失败: {exc.errors()} - 路径: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "请求数据验证失败",
            "details": exc.errors(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器
    
    处理所有未捕获的异常。
    """
    logger.exception(
        f"未处理的异常: {type(exc).__name__} - {str(exc)} - "
        f"路径: {request.url.path}"
    )
    
    # 在生产环境中，不暴露详细的错误信息
    if settings.is_production():
        message = "内部服务器错误"
        details = None
    else:
        message = f"内部服务器错误: {str(exc)}"
        details = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
    )


# ==================== 基础路由 ====================

@app.get("/health", tags=["系统"])
async def health_check() -> Dict[str, Any]:
    """
    健康检查接口
    
    用于检查应用和数据库的健康状态。
    
    Returns:
        dict: 健康状态信息
    """
    health_status = {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
    
    # 检查数据库连接
    try:
        db_healthy = check_connection()
        health_status["database"] = "connected" if db_healthy else "disconnected"
    except Exception as e:
        logger.warning(f"数据库健康检查失败: {e}")
        health_status["database"] = "error"
    
    return success_response(data=health_status, message="服务运行正常")


@app.get("/version", tags=["系统"])
async def get_version() -> Dict[str, Any]:
    """
    版本信息接口
    
    返回应用的版本信息。
    
    Returns:
        dict: 版本信息
    """
    version_info = {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
    
    return success_response(data=version_info, message="版本信息获取成功")


# ==================== WebSocket 路由 ====================

from fastapi import WebSocket, WebSocketDisconnect
from app.websocket import SimpleWebSocketHandler, manager


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket 连接端点
    
    提供 WebSocket 连接功能，支持实时消息推送。
    
    Args:
        websocket: WebSocket 连接对象
        user_id: 用户 ID（从路径参数获取）
        
    Example:
        ```javascript
        // 客户端连接示例
        const ws = new WebSocket('ws://localhost:8000/ws/test_user');
        
        ws.onopen = () => {
            console.log('Connected');
        };
        
        ws.onmessage = (event) => {
            console.log('Received:', JSON.parse(event.data));
        };
        
        ws.onerror = (error) => {
            console.error('Error:', error);
        };
        
        // 发送消息
        ws.send(JSON.stringify({
            type: 'ping',
            timestamp: Date.now()
        }));
        ```
    """
    # 创建处理器并处理连接
    handler = SimpleWebSocketHandler(user_id)
    await handler.handle_connection(websocket)


@app.get("/ws/stats", tags=["WebSocket"])
async def websocket_stats() -> Dict[str, Any]:
    """
    WebSocket 连接统计接口
    
    返回当前 WebSocket 连接的统计信息。
    
    Returns:
        dict: 连接统计信息，包括总连接数、已连接用户数等
    """
    stats = {
        "total_connections": manager.get_total_connections_count(),
        "connected_users_count": len(manager.get_connected_users()),
        "connected_users": list(manager.get_connected_users()),
    }
    
    return success_response(data=stats, message="WebSocket 统计信息获取成功")


# ==================== API 路由注册 ====================

# 这里可以注册其他 API 路由
# 示例：
# from app.api import router as api_router
# app.include_router(api_router, prefix="/api/v1", tags=["API"])


# ==================== 导出 ====================

__all__ = ["app"]

