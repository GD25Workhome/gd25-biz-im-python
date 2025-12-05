"""
WebSocket 基础处理器模块

提供 WebSocket 连接处理的基础框架，包括：
- 连接处理框架
- 消息接收框架
- 扩展接口
"""

import json
import logging
from typing import Optional, Any, Callable, Awaitable, Dict
from fastapi import WebSocket, WebSocketDisconnect

from app.websocket.manager import manager
from app.utils.logger import get_logger

# 配置日志
logger = get_logger(__name__)


class WebSocketHandler:
    """
    WebSocket 基础处理器
    
    提供 WebSocket 连接处理的基础框架，包括连接建立、消息接收、错误处理等。
    子类可以继承此类并重写特定方法来扩展功能。
    """
    
    def __init__(self, user_id: str):
        """
        初始化处理器
        
        Args:
            user_id: 用户 ID
        """
        self.user_id = user_id
        self.websocket: Optional[WebSocket] = None
    
    async def on_connect(self, websocket: WebSocket) -> None:
        """
        连接建立时的处理逻辑
        
        子类可以重写此方法来添加自定义的连接建立逻辑。
        
        Args:
            websocket: WebSocket 连接对象
            
        Example:
            ```python
            class CustomHandler(WebSocketHandler):
                async def on_connect(self, websocket: WebSocket):
                    await super().on_connect(websocket)
                    # 自定义逻辑：发送欢迎消息
                    await websocket.send_text(json.dumps({
                        "type": "welcome",
                        "message": f"欢迎，{self.user_id}！"
                    }))
            ```
        """
        self.websocket = websocket
        await manager.connect(websocket, self.user_id)
        logger.info(f"WebSocket 连接已建立: 用户 {self.user_id}")
    
    async def on_message(self, message: str) -> None:
        """
        接收到消息时的处理逻辑
        
        子类必须重写此方法来处理接收到的消息。
        
        Args:
            message: 接收到的消息文本
            
        Raises:
            NotImplementedError: 如果子类未重写此方法
            
        Example:
            ```python
            class CustomHandler(WebSocketHandler):
                async def on_message(self, message: str):
                    try:
                        data = json.loads(message)
                        message_type = data.get("type")
                        
                        if message_type == "ping":
                            await self.send_pong()
                        elif message_type == "chat":
                            await self.handle_chat(data)
                    except json.JSONDecodeError:
                        await self.send_error("消息格式错误")
            ```
        """
        raise NotImplementedError("子类必须实现 on_message 方法")
    
    async def on_disconnect(self) -> None:
        """
        连接断开时的处理逻辑
        
        子类可以重写此方法来添加自定义的断开连接逻辑。
        
        Example:
            ```python
            class CustomHandler(WebSocketHandler):
                async def on_disconnect(self):
                    # 自定义逻辑：清理用户状态
                    await self.cleanup_user_state()
                    await super().on_disconnect()
            ```
        """
        if self.websocket:
            manager.disconnect(self.websocket)
        logger.info(f"WebSocket 连接已断开: 用户 {self.user_id}")
    
    async def on_error(self, error: Exception) -> None:
        """
        发生错误时的处理逻辑
        
        子类可以重写此方法来添加自定义的错误处理逻辑。
        
        Args:
            error: 发生的异常对象
            
        Example:
            ```python
            class CustomHandler(WebSocketHandler):
                async def on_error(self, error: Exception):
                    logger.error(f"WebSocket 错误: {error}")
                    await self.send_error("处理消息时发生错误")
            ```
        """
        logger.error(f"WebSocket 错误 (用户 {self.user_id}): {error}", exc_info=True)
    
    async def send_message(self, message: Any) -> None:
        """
        发送消息给当前连接
        
        Args:
            message: 要发送的消息（可以是字符串、字典等，会自动序列化为 JSON）
            
        Example:
            ```python
            # 发送字符串消息
            await handler.send_message("Hello")
            
            # 发送字典消息
            await handler.send_message({"type": "response", "data": "success"})
            ```
        """
        if not self.websocket:
            logger.warning(f"无法发送消息：用户 {self.user_id} 的连接不存在")
            return
        
        try:
            if isinstance(message, str):
                message_text = message
            else:
                message_text = json.dumps(message, ensure_ascii=False)
            
            await self.websocket.send_text(message_text)
        except Exception as e:
            logger.error(f"发送消息失败 (用户 {self.user_id}): {e}")
            raise
    
    async def send_error(self, error_message: str, error_code: Optional[str] = None) -> None:
        """
        发送错误消息给当前连接
        
        Args:
            error_message: 错误消息
            error_code: 错误代码（可选）
            
        Example:
            ```python
            await handler.send_error("操作失败", "OPERATION_FAILED")
            ```
        """
        error_data = {
            "type": "error",
            "message": error_message,
        }
        if error_code:
            error_data["code"] = error_code
        
        await self.send_message(error_data)
    
    async def handle_connection(self, websocket: WebSocket) -> None:
        """
        处理 WebSocket 连接的完整生命周期
        
        这是主要的入口方法，处理连接的建立、消息接收和断开。
        
        Args:
            websocket: WebSocket 连接对象
            
        Example:
            ```python
            handler = WebSocketHandler("user123")
            await handler.handle_connection(websocket)
            ```
        """
        try:
            # 建立连接
            await self.on_connect(websocket)
            
            # 持续接收消息
            while True:
                try:
                    # 接收消息
                    message = await websocket.receive_text()
                    await self.on_message(message)
                except WebSocketDisconnect:
                    # 正常断开连接
                    break
                except Exception as e:
                    # 处理其他错误
                    await self.on_error(e)
                    # 可以选择继续处理或断开连接
                    # 这里选择断开连接，避免错误循环
                    break
        
        except Exception as e:
            logger.error(f"WebSocket 连接处理异常 (用户 {self.user_id}): {e}", exc_info=True)
            await self.on_error(e)
        finally:
            # 断开连接
            await self.on_disconnect()


class SimpleWebSocketHandler(WebSocketHandler):
    """
    简单的 WebSocket 处理器实现
    
    提供一个基础的实现示例，支持 ping/pong 心跳和简单的消息回显。
    可以作为其他处理器的参考或直接使用。
    """
    
    async def on_connect(self, websocket: WebSocket) -> None:
        """连接建立时发送欢迎消息"""
        await super().on_connect(websocket)
        
        # 发送欢迎消息
        await self.send_message({
            "type": "welcome",
            "message": f"欢迎，{self.user_id}！",
            "user_id": self.user_id,
        })
    
    async def on_message(self, message: str) -> None:
        """处理接收到的消息"""
        try:
            # 尝试解析 JSON 消息
            try:
                data = json.loads(message)
                message_type = data.get("type", "unknown")
            except json.JSONDecodeError:
                # 如果不是 JSON，当作普通文本处理
                data = {"type": "text", "content": message}
                message_type = "text"
            
            # 根据消息类型处理
            if message_type == "ping":
                # 心跳消息
                await self.send_message({
                    "type": "pong",
                    "timestamp": data.get("timestamp"),
                })
            elif message_type == "echo":
                # 回显消息
                await self.send_message({
                    "type": "echo",
                    "content": data.get("content", ""),
                    "original": data,
                })
            else:
                # 默认处理：回显原始消息
                await self.send_message({
                    "type": "message",
                    "content": data,
                    "message": f"收到消息: {message}",
                })
        
        except Exception as e:
            logger.error(f"处理消息失败 (用户 {self.user_id}): {e}")
            await self.send_error("处理消息时发生错误", "MESSAGE_PROCESSING_ERROR")


# 导出
__all__ = ["WebSocketHandler", "SimpleWebSocketHandler"]

