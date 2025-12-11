"""
IM WebSocket 处理器模块

提供 IM 特定的 WebSocket 连接处理，包括消息发送、接收等。
"""

import json
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.websocket.handler import WebSocketHandler
from app.websocket.manager import manager
from app.db.session import get_db_session
from app.services.core.message_service import MessageService
from app.services.core.websocket_service import WebSocketService
from app.schemas.message import MessageCreate
from app.utils.logger import get_logger
from app.utils.exceptions import NotFoundError, ValidationError

# 配置日志
logger = get_logger(__name__)


class IMWebSocketHandler(WebSocketHandler):
    """
    IM WebSocket 处理器
    
    处理 IM 相关的 WebSocket 连接，包括：
    - 连接建立和断开
    - 接收客户端发送的消息
    - 处理 send_message 类型的消息（通过 HTTP API 发送消息）
    - 推送新消息通知
    
    示例：
        ```python
        handler = IMWebSocketHandler("user_001")
        await handler.handle_connection(websocket)
        ```
    """
    
    def __init__(self, user_id: str):
        """
        初始化 IM WebSocket 处理器
        
        Args:
            user_id: 用户 ID
        """
        super().__init__(user_id)
        self.db: Optional[Session] = None
    
    async def on_connect(self, websocket: WebSocket) -> None:
        """
        连接建立时的处理逻辑
        
        建立连接并发送欢迎消息。
        
        Args:
            websocket: WebSocket 连接对象
        """
        await super().on_connect(websocket)
        
        # 发送欢迎消息（不需要数据库会话）
        await self.send_message({
            "type": "welcome",
            "message": f"欢迎，{self.user_id}！",
            "user_id": self.user_id,
        })
    
    async def on_message(self, message: str) -> None:
        """
        处理接收到的消息
        
        支持的消息类型：
        - ping: 心跳消息，返回 pong
        - send_message: 发送消息到群组（需要 group_id 和 content）
        
        Args:
            message: 接收到的消息文本
        """
        try:
            # 解析 JSON 消息
            try:
                data = json.loads(message)
                message_type = data.get("type", "unknown")
            except json.JSONDecodeError:
                await self.send_error("消息格式错误，必须是有效的 JSON", "INVALID_FORMAT")
                return
            
            # 根据消息类型处理
            if message_type == "ping":
                # 心跳消息
                await self.send_message({
                    "type": "pong",
                    "timestamp": data.get("timestamp"),
                })
            elif message_type == "send_message":
                # 发送消息到群组
                await self.handle_send_message(data)
            else:
                # 未知消息类型
                await self.send_error(
                    f"未知的消息类型: {message_type}",
                    "UNKNOWN_MESSAGE_TYPE"
                )
        
        except Exception as e:
            logger.error(f"处理消息失败 (用户 {self.user_id}): {e}", exc_info=True)
            await self.send_error("处理消息时发生错误", "MESSAGE_PROCESSING_ERROR")
    
    async def handle_send_message(self, data: dict) -> None:
        """
        处理发送消息请求
        
        接收客户端发送的消息请求，通过消息服务发送消息，然后推送通知。
        
        Args:
            data: 消息数据，包含 group_id 和 content
            
        Example:
            ```python
            # 客户端发送的消息格式
            {
                "type": "send_message",
                "group_id": "group_001",
                "content": "这是一条消息"
            }
            ```
        """
        try:
            # 验证必需字段
            group_id = data.get("group_id")
            content = data.get("content")
            
            if not group_id:
                await self.send_error("缺少 group_id 字段", "MISSING_GROUP_ID")
                return
            
            if not content:
                await self.send_error("缺少 content 字段", "MISSING_CONTENT")
                return
            
            # 创建消息服务（每次消息处理都创建新的数据库会话，确保事务隔离）
            db = get_db_session()
            try:
                message_service = MessageService(db)
                websocket_service = WebSocketService(db)
                
                # 创建消息
                message_create = MessageCreate(
                    group_id=group_id,
                    content=content
                )
                
                # 发送消息（通过消息服务）
                try:
                    message_response = message_service.send_message(
                        message_create,
                        self.user_id
                    )
                    
                    # 提交事务
                    db.commit()
                    
                    # 推送新消息通知给群组其他成员（排除发送人）
                    await websocket_service.send_message_to_group(
                        group_id=group_id,
                        message={
                            "type": "new_message",
                            "message_id": message_response.message_id,
                            "group_id": message_response.group_id,
                            "from_user_id": message_response.from_user_id,
                            "msg_type": message_response.msg_type,
                            "msg_content": message_response.msg_content,
                            "created_at": message_response.created_at.isoformat(),
                        },
                        exclude_user_id=self.user_id
                    )
                    
                    # 向发送人返回成功响应
                    await self.send_message({
                        "type": "message_sent",
                        "message_id": message_response.message_id,
                        "group_id": message_response.group_id,
                        "content": message_response.msg_content,
                        "created_at": message_response.created_at.isoformat(),
                    })
                    
                except NotFoundError as e:
                    db.rollback()
                    await self.send_error(e.message, "NOT_FOUND")
                except ValidationError as e:
                    db.rollback()
                    await self.send_error(e.message, "VALIDATION_ERROR")
                except Exception as e:
                    db.rollback()
                    logger.error(f"发送消息失败 (用户 {self.user_id}): {e}", exc_info=True)
                    await self.send_error("发送消息失败", "SEND_MESSAGE_FAILED")
            finally:
                # 关闭数据库会话
                db.close()
        
        except Exception as e:
            logger.error(f"处理发送消息请求失败 (用户 {self.user_id}): {e}", exc_info=True)
            await self.send_error("处理发送消息请求时发生错误", "HANDLE_SEND_MESSAGE_ERROR")
    
    async def on_disconnect(self) -> None:
        """
        连接断开时的处理逻辑
        
        清理资源。
        """
        # 清理数据库会话引用（实际会话在每次消息处理时都会关闭）
        self.db = None
        
        await super().on_disconnect()
