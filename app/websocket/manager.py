"""
WebSocket 连接管理器模块

提供 WebSocket 连接的管理功能，包括：
- 连接注册和注销
- 个人消息推送
- 广播消息推送
- 连接状态跟踪
"""

import json
import logging
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket

from app.utils.logger import get_logger

# 配置日志
logger = get_logger(__name__)


class ConnectionManager:
    """
    WebSocket 连接管理器
    
    管理所有活跃的 WebSocket 连接，提供连接注册、注销、消息推送等功能。
    支持按用户 ID 管理连接，一个用户可以拥有多个连接（多设备登录）。
    """
    
    def __init__(self):
        """
        初始化连接管理器
        
        使用字典存储连接，key 为用户 ID，value 为 WebSocket 连接集合。
        这样可以支持一个用户多个连接（多设备登录）。
        """
        # 存储格式：{user_id: {websocket1, websocket2, ...}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # 反向映射：{websocket: user_id}，用于快速查找连接所属的用户
        self.connection_to_user: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """
        注册 WebSocket 连接
        
        将新的 WebSocket 连接注册到管理器中，并建立用户 ID 与连接的映射关系。
        
        Args:
            websocket: WebSocket 连接对象
            user_id: 用户 ID（用于标识连接所属的用户）
            
        Example:
            ```python
            manager = ConnectionManager()
            await manager.connect(websocket, "user123")
            ```
        """
        # 接受 WebSocket 连接
        await websocket.accept()
        
        # 注册连接
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_to_user[websocket] = user_id
        
        logger.info(f"WebSocket 连接已注册: 用户 {user_id}, 当前连接数: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket) -> Optional[str]:
        """
        注销 WebSocket 连接
        
        从管理器中移除指定的 WebSocket 连接。
        
        Args:
            websocket: 要注销的 WebSocket 连接对象
            
        Returns:
            Optional[str]: 被注销连接的用户 ID，如果连接不存在则返回 None
            
        Example:
            ```python
            user_id = manager.disconnect(websocket)
            ```
        """
        # 获取连接所属的用户 ID
        user_id = self.connection_to_user.get(websocket)
        
        if user_id:
            # 从用户连接集合中移除
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                
                # 如果用户没有其他连接，删除用户记录
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # 从反向映射中移除
            self.connection_to_user.pop(websocket, None)
            
            logger.info(f"WebSocket 连接已注销: 用户 {user_id}")
        
        return user_id
    
    async def send_personal_message(self, message: Any, user_id: str) -> bool:
        """
        向指定用户发送个人消息
        
        向指定用户的所有活跃连接发送消息。如果用户没有活跃连接，返回 False。
        
        Args:
            message: 要发送的消息（可以是字符串、字典等，会自动序列化为 JSON）
            user_id: 目标用户 ID
            
        Returns:
            bool: 是否成功发送（如果用户没有活跃连接，返回 False）
            
        Example:
            ```python
            # 发送字符串消息
            await manager.send_personal_message("Hello", "user123")
            
            # 发送字典消息
            await manager.send_personal_message({"type": "notification", "content": "新消息"}, "user123")
            ```
        """
        if user_id not in self.active_connections:
            logger.warning(f"用户 {user_id} 没有活跃的 WebSocket 连接")
            return False
        
        # 序列化消息
        if isinstance(message, str):
            message_text = message
        else:
            message_text = json.dumps(message, ensure_ascii=False)
        
        # 向用户的所有连接发送消息
        disconnected_connections = set()
        success_count = 0
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(message_text)
                success_count += 1
            except Exception as e:
                logger.error(f"向用户 {user_id} 发送消息失败: {e}")
                # 标记为断开连接
                disconnected_connections.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected_connections:
            self.disconnect(websocket)
        
        if success_count > 0:
            logger.info(f"向用户 {user_id} 发送消息成功，成功连接数: {success_count}")
            return True
        else:
            logger.warning(f"向用户 {user_id} 发送消息失败，所有连接已断开")
            return False
    
    async def broadcast(self, message: Any, exclude_user: Optional[str] = None) -> int:
        """
        广播消息给所有连接的客户端
        
        向所有活跃连接发送消息，可以选择排除特定用户。
        
        Args:
            message: 要发送的消息（可以是字符串、字典等，会自动序列化为 JSON）
            exclude_user: 要排除的用户 ID（可选），该用户不会收到广播消息
            
        Returns:
            int: 成功发送的连接数
            
        Example:
            ```python
            # 广播给所有用户
            count = await manager.broadcast({"type": "announcement", "content": "系统通知"})
            
            # 广播给除指定用户外的所有用户
            count = await manager.broadcast("系统消息", exclude_user="user123")
            ```
        """
        # 序列化消息
        if isinstance(message, str):
            message_text = message
        else:
            message_text = json.dumps(message, ensure_ascii=False)
        
        # 收集所有连接
        all_connections = []
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            all_connections.extend(connections)
        
        # 发送消息
        disconnected_connections = set()
        success_count = 0
        
        for websocket in all_connections:
            try:
                await websocket.send_text(message_text)
                success_count += 1
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                # 标记为断开连接
                disconnected_connections.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected_connections:
            self.disconnect(websocket)
        
        logger.info(f"广播消息完成，成功连接数: {success_count}")
        return success_count
    
    def get_user_connections_count(self, user_id: str) -> int:
        """
        获取指定用户的连接数
        
        Args:
            user_id: 用户 ID
            
        Returns:
            int: 用户的活跃连接数
        """
        if user_id not in self.active_connections:
            return 0
        return len(self.active_connections[user_id])
    
    def get_total_connections_count(self) -> int:
        """
        获取总连接数
        
        Returns:
            int: 所有用户的活跃连接总数
        """
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_connected_users(self) -> Set[str]:
        """
        获取所有已连接的用户 ID 列表
        
        Returns:
            Set[str]: 所有已连接的用户 ID 集合
        """
        return set(self.active_connections.keys())
    
    def is_user_connected(self, user_id: str) -> bool:
        """
        检查用户是否已连接
        
        Args:
            user_id: 用户 ID
            
        Returns:
            bool: 用户是否有活跃连接
        """
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# 创建全局连接管理器实例
# 在应用启动时创建，所有 WebSocket 路由共享此实例
manager = ConnectionManager()


# 导出
__all__ = ["ConnectionManager", "manager"]

