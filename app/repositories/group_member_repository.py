"""
群组成员 Repository

提供群组成员数据访问层，继承自 BaseRepository。
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.group_member import GroupMember
from app.repositories.base import BaseRepository


class GroupMemberRepository(BaseRepository[GroupMember]):
    """
    群组成员 Repository
    
    继承自 BaseRepository，提供群组成员相关的数据访问方法。
    
    示例：
        ```python
        from app.repositories.group_member_repository import GroupMemberRepository
        from app.db.session import get_db_session
        
        db = get_db_session()
        repo = GroupMemberRepository(db)
        
        # 添加成员
        member = repo.add_member(
            group_id="group_001",
            user_id="user_001",
            user_role="PATIENT"
        )
        
        # 获取成员
        member = repo.get_member("group_001", "user_001")
        
        # 获取群组所有成员
        members = repo.get_members_by_group("group_001")
        
        # 移除成员
        success = repo.remove_member("group_001", "user_001")
        ```
    """
    
    def __init__(self, db: Session):
        super().__init__(GroupMember, db)
    
    def add_member(
        self,
        group_id: str,
        user_id: str,
        user_role: str
    ) -> GroupMember:
        """
        添加群组成员
        
        Args:
            group_id: 群组ID
            user_id: 用户ID
            user_role: 用户在群组中的身份标签（PATIENT/DOCTOR/AI_ASSISTANT）
            
        Returns:
            GroupMember: 创建的群组成员对象
            
        Raises:
            IntegrityError: 如果用户已在群组中（联合唯一约束）
        """
        member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            user_role=user_role
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member
    
    def get_member(
        self,
        group_id: str,
        user_id: str
    ) -> Optional[GroupMember]:
        """
        获取群组成员
        
        Args:
            group_id: 群组ID
            user_id: 用户ID
            
        Returns:
            Optional[GroupMember]: 群组成员对象，如果不存在返回 None
        """
        return self.db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        ).first()
    
    def get_members_by_group(self, group_id: str) -> List[GroupMember]:
        """
        获取群组的所有成员
        
        Args:
            group_id: 群组ID
            
        Returns:
            List[GroupMember]: 群组成员列表
        """
        return self.db.query(GroupMember).filter(
            GroupMember.group_id == group_id
        ).order_by(GroupMember.joined_at).all()
    
    def remove_member(
        self,
        group_id: str,
        user_id: str
    ) -> bool:
        """
        移除群组成员
        
        Args:
            group_id: 群组ID
            user_id: 用户ID
            
        Returns:
            bool: 是否移除成功（如果成员不存在返回 False）
        """
        member = self.get_member(group_id, user_id)
        if not member:
            return False
        
        self.db.delete(member)
        self.db.commit()
        return True
    
    def get_groups_by_user(self, user_id: str) -> List[GroupMember]:
        """
        获取用户所在的所有群组
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[GroupMember]: 群组成员列表（每个成员代表一个群组）
        """
        return self.db.query(GroupMember).filter(
            GroupMember.user_id == user_id
        ).order_by(GroupMember.joined_at).all()
    
    def get_members_by_role(
        self,
        group_id: str,
        user_role: str
    ) -> List[GroupMember]:
        """
        获取群组中指定身份的所有成员
        
        Args:
            group_id: 群组ID
            user_role: 用户身份（PATIENT/DOCTOR/AI_ASSISTANT）
            
        Returns:
            List[GroupMember]: 群组成员列表
        """
        return self.db.query(GroupMember).filter(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_role == user_role
            )
        ).order_by(GroupMember.joined_at).all()
