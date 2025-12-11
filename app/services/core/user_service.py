"""
用户服务层

提供用户相关的业务逻辑处理，包括用户创建、查询、更新等。
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError
from app.utils.id_generator import generate_user_id


class UserService:
    """
    用户服务
    
    处理用户相关的业务逻辑，包括：
    - 用户创建和验证
    - 用户查询
    - 用户身份更新
    - 业务规则验证
    
    示例：
        ```python
        from app.services.core.user_service import UserService
        from app.db.session import get_db
        
        db = next(get_db())
        service = UserService(db)
        
        # 创建用户
        user_response = service.create_user(UserCreate(
            username="张三",
            user_role="PATIENT"
        ))
        
        # 获取用户
        user_response = service.get_user("user_001")
        
        # 更新用户身份
        user_response = service.update_user_role("user_001", "DOCTOR")
        ```
    """
    
    def __init__(self, db: Session):
        """
        初始化用户服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.repository = UserRepository(db)
    
    def create_user(self, user_create: UserCreate) -> UserResponse:
        """
        创建用户
        
        Args:
            user_create: 用户创建数据
            
        Returns:
            UserResponse: 创建的用户信息
            
        Raises:
            ValidationError: 当user_role无效时抛出
            ConflictError: 当user_id已存在时抛出
        """
        # 验证user_role
        valid_roles = ["PATIENT", "DOCTOR", "AI_ASSISTANT"]
        if user_create.user_role not in valid_roles:
            raise ValidationError(
                f"无效的用户身份: {user_create.user_role}，必须是 {valid_roles} 之一"
            )
        
        # 生成user_id
        user_id = generate_user_id()
        
        # 创建用户
        try:
            user = self.repository.create(
                user_id=user_id,
                username=user_create.username,
                user_role=user_create.user_role
            )
            return UserResponse.model_validate(user)
        except IntegrityError as e:
            self.db.rollback()
            # 如果user_id冲突，重新生成（理论上不应该发生）
            if "user_id" in str(e).lower() or "unique" in str(e).lower():
                raise ConflictError(f"用户ID冲突，请重试: {str(e)}")
            raise ValidationError(f"创建用户失败: {str(e)}")
    
    def get_user(self, user_id: str) -> Optional[UserResponse]:
        """
        获取用户信息
        
        Args:
            user_id: 用户唯一标识
            
        Returns:
            Optional[UserResponse]: 用户信息，如果不存在返回 None
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)
    
    def update_user_role(self, user_id: str, new_role: str) -> UserResponse:
        """
        更新用户身份标签
        
        Args:
            user_id: 用户唯一标识
            new_role: 新的用户身份（PATIENT/DOCTOR/AI_ASSISTANT）
            
        Returns:
            UserResponse: 更新后的用户信息
            
        Raises:
            NotFoundError: 当用户不存在时抛出
            ValidationError: 当new_role无效时抛出
        """
        # 验证new_role
        valid_roles = ["PATIENT", "DOCTOR", "AI_ASSISTANT"]
        if new_role not in valid_roles:
            raise ValidationError(
                f"无效的用户身份: {new_role}，必须是 {valid_roles} 之一"
            )
        
        # 获取用户
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"用户 {user_id} 不存在")
        
        # 更新用户身份
        user.user_role = new_role
        updated_user = self.repository.update(user)
        
        return UserResponse.model_validate(updated_user)
