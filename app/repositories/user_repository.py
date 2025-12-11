"""
用户 Repository

提供用户数据访问层，继承自 BaseRepository。
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    用户 Repository
    
    继承自 BaseRepository，提供用户相关的数据访问方法。
    
    示例：
        ```python
        from app.repositories.user_repository import UserRepository
        from app.db.session import get_db_session
        
        db = get_db_session()
        repo = UserRepository(db)
        
        # 创建用户
        user = repo.create(user_id="user_001", username="张三", user_role="PATIENT")
        
        # 根据 user_id 查询
        user = repo.get_by_id("user_001")
        
        # 更新用户
        user.username = "李四"
        updated_user = repo.update(user)
        ```
    """
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def create(
        self,
        user_id: str,
        username: str,
        user_role: str = "PATIENT"
    ) -> User:
        """
        创建用户
        
        Args:
            user_id: 用户唯一标识
            username: 用户名
            user_role: 用户身份，默认为 PATIENT
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            IntegrityError: 如果 user_id 已存在
        """
        user = User(
            user_id=user_id,
            username=username,
            user_role=user_role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        根据 user_id 获取用户
        
        Args:
            user_id: 用户唯一标识
            
        Returns:
            Optional[User]: 用户对象，如果不存在返回 None
        """
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def update(self, user: User) -> User:
        """
        更新用户
        
        Args:
            user: 用户对象（已修改）
            
        Returns:
            User: 更新后的用户对象
        """
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_role(self, user_role: str) -> list[User]:
        """
        根据用户身份获取用户列表
        
        Args:
            user_role: 用户身份（PATIENT/DOCTOR/AI_ASSISTANT）
            
        Returns:
            list[User]: 用户列表
        """
        return self.db.query(User).filter(User.user_role == user_role).all()
