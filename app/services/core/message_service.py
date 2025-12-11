"""
消息服务层

提供消息相关的业务逻辑处理，包括消息发送、查询等。
"""

from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.message_repository import MessageRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.group_member_repository import GroupMemberRepository
from app.schemas.message import MessageCreate, MessageResponse, MessageListResponse
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError
from app.utils.id_generator import generate_message_id


class MessageService:
    """
    消息服务
    
    处理消息相关的业务逻辑，包括：
    - 消息发送（验证群组存在、发送人在群组中）
    - 消息查询（单条、列表分页）
    - 业务规则验证
    
    示例：
        ```python
        from app.services.core.message_service import MessageService
        from app.db.session import get_db
        
        db = next(get_db())
        service = MessageService(db)
        
        # 发送消息
        message_response = service.send_message(
            MessageCreate(group_id="group_001", content="你好"),
            from_user_id="user_001"
        )
        
        # 获取消息
        message_response = service.get_message("msg_001")
        
        # 获取消息列表（分页）
        messages, total = service.get_messages("group_001", page=1, page_size=20)
        ```
    """
    
    def __init__(self, db: Session):
        """
        初始化消息服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.message_repo = MessageRepository(db)
        self.group_repo = GroupRepository(db)
        self.member_repo = GroupMemberRepository(db)
    
    def send_message(
        self,
        message_create: MessageCreate,
        from_user_id: str
    ) -> MessageResponse:
        """
        发送消息
        
        验证群组是否存在，以及发送人是否在群组中。
        
        Args:
            message_create: 消息创建数据
            from_user_id: 发送人ID
            
        Returns:
            MessageResponse: 创建的消息信息
            
        Raises:
            NotFoundError: 当群组不存在或发送人不在群组中时抛出
            ValidationError: 当创建失败时抛出
        """
        # 验证群组是否存在
        group = self.group_repo.get_by_id(message_create.group_id)
        if not group:
            raise NotFoundError(f"群组 {message_create.group_id} 不存在")
        
        # 验证发送人是否在群组中
        member = self.member_repo.get_member(message_create.group_id, from_user_id)
        if not member:
            raise NotFoundError(
                f"用户 {from_user_id} 不在群组 {message_create.group_id} 中"
            )
        
        # 生成message_id
        message_id = generate_message_id()
        
        # 创建消息
        try:
            message = self.message_repo.create(
                message_id=message_id,
                group_id=message_create.group_id,
                from_user_id=from_user_id,
                msg_type="TEXT",  # 默认消息类型为TEXT
                msg_content=message_create.content
            )
            return MessageResponse.model_validate(message)
        except IntegrityError as e:
            self.db.rollback()
            if "message_id" in str(e).lower() or "unique" in str(e).lower():
                raise ConflictError(f"消息ID冲突，请重试: {str(e)}")
            raise ValidationError(f"发送消息失败: {str(e)}")
    
    def get_message(self, message_id: str) -> MessageResponse:
        """
        获取单条消息
        
        Args:
            message_id: 消息唯一标识
            
        Returns:
            MessageResponse: 消息信息
            
        Raises:
            NotFoundError: 当消息不存在时抛出
        """
        message = self.message_repo.get_by_id(message_id)
        if not message:
            raise NotFoundError(f"消息 {message_id} 不存在")
        
        return MessageResponse.model_validate(message)
    
    def get_messages(
        self,
        group_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[MessageResponse], int]:
        """
        获取消息列表（分页）
        
        Args:
            group_id: 群组ID
            page: 页码（从1开始）
            page_size: 每页数量（1-100）
            
        Returns:
            Tuple[List[MessageResponse], int]: (消息列表, 总记录数)
            
        Raises:
            NotFoundError: 当群组不存在时抛出
            ValidationError: 当分页参数无效时抛出
        """
        # 验证群组是否存在
        group = self.group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundError(f"群组 {group_id} 不存在")
        
        # 验证分页参数
        if page < 1:
            raise ValidationError("页码必须 >= 1")
        
        if page_size < 1 or page_size > 100:
            raise ValidationError("每页数量必须在 1-100 之间")
        
        # 获取消息列表
        messages, total = self.message_repo.get_by_group(
            group_id=group_id,
            page=page,
            page_size=page_size
        )
        
        # 转换为MessageResponse列表
        message_responses = [
            MessageResponse.model_validate(msg) for msg in messages
        ]
        
        return message_responses, total
