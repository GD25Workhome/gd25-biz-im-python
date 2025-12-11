"""
消息 Repository

提供消息数据访问层，继承自 BaseRepository。
"""

from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """
    消息 Repository
    
    继承自 BaseRepository，提供消息相关的数据访问方法。
    
    示例：
        ```python
        from app.repositories.message_repository import MessageRepository
        from app.db.session import get_db_session
        
        db = get_db_session()
        repo = MessageRepository(db)
        
        # 创建消息
        message = repo.create(
            message_id="msg_001",
            group_id="group_001",
            from_user_id="user_001",
            msg_type="TEXT",
            msg_content="这是一条消息"
        )
        
        # 根据 message_id 查询
        message = repo.get_by_id("msg_001")
        
        # 获取群组消息（分页）
        messages, total = repo.get_by_group("group_001", page=1, page_size=20)
        ```
    """
    
    def __init__(self, db: Session):
        super().__init__(Message, db)
    
    def create(
        self,
        message_id: str,
        group_id: str,
        from_user_id: str,
        msg_type: str,
        msg_content: str
    ) -> Message:
        """
        创建消息
        
        Args:
            message_id: 消息唯一标识
            group_id: 群组ID
            from_user_id: 发送人ID
            msg_type: 消息类型（TEXT/IMAGE/AI_REPLY）
            msg_content: 消息内容
            
        Returns:
            Message: 创建的消息对象
            
        Raises:
            IntegrityError: 如果 message_id 已存在
        """
        message = Message(
            message_id=message_id,
            group_id=group_id,
            from_user_id=from_user_id,
            msg_type=msg_type,
            msg_content=msg_content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_by_id(self, message_id: str) -> Optional[Message]:
        """
        根据 message_id 获取消息
        
        Args:
            message_id: 消息唯一标识
            
        Returns:
            Optional[Message]: 消息对象，如果不存在返回 None
        """
        return self.db.query(Message).filter(
            Message.message_id == message_id
        ).first()
    
    def get_by_group(
        self,
        group_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Message], int]:
        """
        获取群组消息（分页）
        
        Args:
            group_id: 群组ID
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            Tuple[List[Message], int]: (消息列表, 总记录数)
        """
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询总数
        total = self.db.query(Message).filter(
            Message.group_id == group_id
        ).count()
        
        # 查询消息列表（按创建时间倒序）
        messages = self.db.query(Message).filter(
            Message.group_id == group_id
        ).order_by(desc(Message.created_at)).offset(offset).limit(page_size).all()
        
        return messages, total
    
    def get_by_user(
        self,
        from_user_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        获取用户发送的消息
        
        Args:
            from_user_id: 发送人ID
            limit: 限制返回数量（可选）
            
        Returns:
            List[Message]: 消息列表（按创建时间倒序）
        """
        query = self.db.query(Message).filter(
            Message.from_user_id == from_user_id
        ).order_by(desc(Message.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_recent_messages(
        self,
        group_id: str,
        limit: int = 10
    ) -> List[Message]:
        """
        获取群组最近的消息
        
        Args:
            group_id: 群组ID
            limit: 返回数量，默认10条
            
        Returns:
            List[Message]: 消息列表（按创建时间倒序）
        """
        return self.db.query(Message).filter(
            Message.group_id == group_id
        ).order_by(desc(Message.created_at)).limit(limit).all()
