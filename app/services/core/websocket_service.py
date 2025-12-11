"""
WebSocket 服务层

提供 WebSocket 实时消息推送相关的业务逻辑处理。
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.websocket.manager import manager
from app.repositories.group_member_repository import GroupMemberRepository
from app.utils.logger import get_logger

# 配置日志
logger = get_logger(__name__)


class WebSocketService:
    """
    WebSocket 服务
    
    处理 WebSocket 实时消息推送相关的业务逻辑，包括：
    - 向群组推送消息（推送给群组所有成员）
    - 向用户推送消息（推送给指定用户）
    - 消息格式统一
    
    示例：
        ```python
        from app.services.core.websocket_service import WebSocketService
        from app.db.session import get_db
        
        db = next(get_db())
        service = WebSocketService(db)
        
        # 向群组推送消息
        count = await service.send_message_to_group(
            group_id="group_001",
            message={"type": "new_message", "content": "新消息"},
            exclude_user_id="user_001"  # 可选，排除发送人
        )
        
        # 向用户推送消息
        success = await service.send_message_to_user(
            user_id="user_001",
            message={"type": "notification", "content": "通知"}
        )
        ```
    """
    
    def __init__(self, db: Session):
        """
        初始化 WebSocket 服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.member_repo = GroupMemberRepository(db)
    
    async def send_message_to_group(
        self,
        group_id: str,
        message: Dict[str, Any],
        exclude_user_id: Optional[str] = None
    ) -> int:
        """
        向群组所有成员推送消息
        
        获取群组的所有成员，然后向每个成员推送消息（排除指定用户）。
        
        Args:
            group_id: 群组ID
            message: 要推送的消息（字典格式）
            exclude_user_id: 要排除的用户ID（可选），通常用于排除消息发送人
            
        Returns:
            int: 成功推送的用户数
            
        Example:
            ```python
            # 推送新消息通知给群组所有成员（排除发送人）
            count = await service.send_message_to_group(
                group_id="group_001",
                message={
                    "type": "new_message",
                    "message_id": "msg_001",
                    "group_id": "group_001",
                    "from_user_id": "user_001",
                    "content": "这是一条新消息"
                },
                exclude_user_id="user_001"
            )
            ```
        """
        # 获取群组所有成员
        members = self.member_repo.get_members_by_group(group_id)
        
        if not members:
            logger.warning(f"群组 {group_id} 没有成员")
            return 0
        
        # 统一消息格式
        formatted_message = self._format_message(message)
        
        # 向每个成员推送消息
        success_count = 0
        for member in members:
            # 排除指定用户
            if exclude_user_id and member.user_id == exclude_user_id:
                continue
            
            # 推送消息
            success = await manager.send_personal_message(
                formatted_message,
                member.user_id
            )
            if success:
                success_count += 1
        
        logger.info(
            f"向群组 {group_id} 推送消息完成，成功推送给 {success_count} 个用户"
        )
        
        return success_count
    
    async def send_message_to_user(
        self,
        user_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        向指定用户推送消息
        
        Args:
            user_id: 目标用户ID
            message: 要推送的消息（字典格式）
            
        Returns:
            bool: 是否成功推送
            
        Example:
            ```python
            # 推送通知给用户
            success = await service.send_message_to_user(
                user_id="user_001",
                message={
                    "type": "notification",
                    "content": "您有一条新消息"
                }
            )
            ```
        """
        # 统一消息格式
        formatted_message = self._format_message(message)
        
        # 推送消息
        success = await manager.send_personal_message(
            formatted_message,
            user_id
        )
        
        if success:
            logger.info(f"向用户 {user_id} 推送消息成功")
        else:
            logger.warning(f"向用户 {user_id} 推送消息失败（用户未连接）")
        
        return success
    
    def _format_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一消息格式
        
        确保所有推送的消息都有一致的格式。
        
        Args:
            message: 原始消息字典
            
        Returns:
            Dict[str, Any]: 格式化后的消息字典
        """
        # 确保消息包含 type 字段
        if "type" not in message:
            message["type"] = "message"
        
        # 添加时间戳（如果不存在）
        if "timestamp" not in message:
            from datetime import datetime
            message["timestamp"] = datetime.now().isoformat()
        
        return message
