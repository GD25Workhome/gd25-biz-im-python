"""
群组 Repository

提供群组数据访问层，继承自 BaseRepository。
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.group import Group
from app.repositories.base import BaseRepository


class GroupRepository(BaseRepository[Group]):
    """
    群组 Repository
    
    继承自 BaseRepository，提供群组相关的数据访问方法。
    
    示例：
        ```python
        from app.repositories.group_repository import GroupRepository
        from app.db.session import get_db_session
        
        db = get_db_session()
        repo = GroupRepository(db)
        
        # 创建群组
        group = repo.create(
            group_id="group_001",
            group_name="医疗咨询群",
            description="患者和医生的咨询群组",
            created_by="user_001"
        )
        
        # 根据 group_id 查询
        group = repo.get_by_id("group_001")
        
        # 更新群组
        group.group_name = "新群组名"
        updated_group = repo.update(group)
        ```
    """
    
    def __init__(self, db: Session):
        super().__init__(Group, db)
    
    def create(
        self,
        group_id: str,
        group_name: str,
        description: Optional[str] = None,
        created_by: str = ""
    ) -> Group:
        """
        创建群组
        
        Args:
            group_id: 群组唯一标识
            group_name: 群组名称
            description: 群组描述（可选）
            created_by: 创建人ID
            
        Returns:
            Group: 创建的群组对象
            
        Raises:
            IntegrityError: 如果 group_id 已存在
        """
        group = Group(
            group_id=group_id,
            group_name=group_name,
            description=description,
            created_by=created_by
        )
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group
    
    def get_by_id(self, group_id: str) -> Optional[Group]:
        """
        根据 group_id 获取群组
        
        Args:
            group_id: 群组唯一标识
            
        Returns:
            Optional[Group]: 群组对象，如果不存在返回 None
        """
        return self.db.query(Group).filter(Group.group_id == group_id).first()
    
    def update(self, group: Group) -> Group:
        """
        更新群组
        
        Args:
            group: 群组对象（已修改）
            
        Returns:
            Group: 更新后的群组对象
        """
        self.db.commit()
        self.db.refresh(group)
        return group
    
    def get_by_creator(self, created_by: str) -> list[Group]:
        """
        根据创建人获取群组列表
        
        Args:
            created_by: 创建人ID
            
        Returns:
            list[Group]: 群组列表
        """
        return self.db.query(Group).filter(Group.created_by == created_by).all()
