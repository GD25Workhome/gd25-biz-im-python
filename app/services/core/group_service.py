"""
群组服务层

提供群组相关的业务逻辑处理，包括群组创建、成员管理等。
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.group_repository import GroupRepository
from app.repositories.group_member_repository import GroupMemberRepository
from app.repositories.user_repository import UserRepository
from app.schemas.group import GroupCreate, GroupResponse, GroupMemberAdd
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError
from app.utils.id_generator import generate_group_id


class GroupService:
    """
    群组服务
    
    处理群组相关的业务逻辑，包括：
    - 群组创建（自动添加创建人为成员，身份为DOCTOR）
    - 群组查询
    - 群组成员管理
    - 业务规则验证
    
    示例：
        ```python
        from app.services.core.group_service import GroupService
        from app.db.session import get_db
        
        db = next(get_db())
        service = GroupService(db)
        
        # 创建群组
        group_response = service.create_group(
            GroupCreate(group_name="医疗咨询群", description="测试"),
            creator_id="user_001"
        )
        
        # 添加成员
        success = service.add_member("group_001", GroupMemberAdd(
            user_id="user_002",
            user_role="PATIENT"
        ))
        
        # 获取群组成员列表
        members = service.get_group_members("group_001")
        ```
    """
    
    def __init__(self, db: Session):
        """
        初始化群组服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.group_repo = GroupRepository(db)
        self.member_repo = GroupMemberRepository(db)
        self.user_repo = UserRepository(db)
    
    def create_group(
        self,
        group_create: GroupCreate,
        creator_id: str
    ) -> GroupResponse:
        """
        创建群组
        
        创建群组时，会自动将创建人添加为群组成员，身份为DOCTOR。
        
        Args:
            group_create: 群组创建数据
            creator_id: 创建人ID
            
        Returns:
            GroupResponse: 创建的群组信息
            
        Raises:
            NotFoundError: 当创建人不存在时抛出
            ValidationError: 当创建失败时抛出
        """
        # 验证创建人是否存在
        creator = self.user_repo.get_by_id(creator_id)
        if not creator:
            raise NotFoundError(f"创建人 {creator_id} 不存在")
        
        # 生成group_id
        group_id = generate_group_id()
        
        # 创建群组
        try:
            group = self.group_repo.create(
                group_id=group_id,
                group_name=group_create.group_name,
                description=group_create.description,
                created_by=creator_id
            )
            
            # 自动添加创建人为成员，身份为DOCTOR
            try:
                self.member_repo.add_member(
                    group_id=group_id,
                    user_id=creator_id,
                    user_role="DOCTOR"
                )
            except IntegrityError:
                # 如果创建人已经在群组中（理论上不应该发生），忽略错误
                self.db.rollback()
                pass
            
            return GroupResponse.model_validate(group)
        except IntegrityError as e:
            self.db.rollback()
            if "group_id" in str(e).lower() or "unique" in str(e).lower():
                raise ConflictError(f"群组ID冲突，请重试: {str(e)}")
            raise ValidationError(f"创建群组失败: {str(e)}")
    
    def get_group(self, group_id: str) -> Optional[GroupResponse]:
        """
        获取群组信息
        
        Args:
            group_id: 群组唯一标识
            
        Returns:
            Optional[GroupResponse]: 群组信息，如果不存在返回 None
        """
        group = self.group_repo.get_by_id(group_id)
        if not group:
            return None
        return GroupResponse.model_validate(group)
    
    def add_member(
        self,
        group_id: str,
        member_add: GroupMemberAdd
    ) -> bool:
        """
        添加群组成员
        
        Args:
            group_id: 群组ID
            member_add: 成员添加数据
            
        Returns:
            bool: 是否添加成功
            
        Raises:
            NotFoundError: 当群组不存在或用户不存在时抛出
            ConflictError: 当用户已在群组中时抛出
            ValidationError: 当user_role无效时抛出
        """
        # 验证群组是否存在
        group = self.group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundError(f"群组 {group_id} 不存在")
        
        # 验证用户是否存在
        user = self.user_repo.get_by_id(member_add.user_id)
        if not user:
            raise NotFoundError(f"用户 {member_add.user_id} 不存在")
        
        # 验证user_role
        valid_roles = ["PATIENT", "DOCTOR", "AI_ASSISTANT"]
        if member_add.user_role not in valid_roles:
            raise ValidationError(
                f"无效的用户身份: {member_add.user_role}，必须是 {valid_roles} 之一"
            )
        
        # 检查用户是否已在群组中
        existing_member = self.member_repo.get_member(group_id, member_add.user_id)
        if existing_member:
            raise ConflictError(f"用户 {member_add.user_id} 已在群组 {group_id} 中")
        
        # 添加成员
        try:
            self.member_repo.add_member(
                group_id=group_id,
                user_id=member_add.user_id,
                user_role=member_add.user_role
            )
            return True
        except IntegrityError as e:
            self.db.rollback()
            if "unique" in str(e).lower() or "uk_group_user" in str(e).lower():
                raise ConflictError(f"用户 {member_add.user_id} 已在群组 {group_id} 中")
            raise ValidationError(f"添加成员失败: {str(e)}")
    
    def get_group_members(self, group_id: str) -> List[Dict]:
        """
        获取群组成员列表
        
        Args:
            group_id: 群组ID
            
        Returns:
            List[Dict]: 成员列表，每个成员包含 user_id, user_role, joined_at
            
        Raises:
            NotFoundError: 当群组不存在时抛出
        """
        # 验证群组是否存在
        group = self.group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundError(f"群组 {group_id} 不存在")
        
        # 获取成员列表
        members = self.member_repo.get_members_by_group(group_id)
        
        # 转换为字典列表
        result = []
        for member in members:
            result.append({
                "user_id": member.user_id,
                "user_role": member.user_role,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None
            })
        
        return result
