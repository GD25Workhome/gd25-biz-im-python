"""
用户服务示例

展示如何实现业务逻辑层，协调 Repository 和业务规则。
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.utils.exceptions import NotFoundError, ValidationError


class UserService:
    """
    用户服务
    
    处理用户相关的业务逻辑，包括：
    - 用户创建和验证
    - 用户更新
    - 用户查询
    - 业务规则验证
    
    示例：
        ```python
        from app.services.user_service import UserService
        from app.db.session import get_db
        
        db = next(get_db())
        service = UserService(db)
        
        # 创建用户
        user = service.create_user(UserCreate(
            name="张三",
            email="zhangsan@example.com",
            age=25
        ))
        
        # 获取用户
        user = service.get_user_by_id(user.id)
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
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        创建用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            ValidationError: 当邮箱已存在时抛出
        """
        # 检查邮箱是否已存在
        existing_user = self.repository.get_by_email(user_data.email)
        if existing_user:
            raise ValidationError(f"邮箱 {user_data.email} 已被使用")
        
        # 创建用户
        try:
            user = self.repository.create(user_data.model_dump())
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise ValidationError(f"创建用户失败: {str(e)}")
    
    def get_user_by_id(self, user_id: int) -> User:
        """
        根据 ID 获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User: 用户对象
            
        Raises:
            NotFoundError: 当用户不存在时抛出
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"用户 ID {user_id} 不存在")
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            Optional[User]: 用户对象，如果不存在返回 None
        """
        return self.repository.get_by_email(email)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        更新用户
        
        Args:
            user_id: 用户ID
            user_data: 用户更新数据
            
        Returns:
            User: 更新后的用户对象
            
        Raises:
            NotFoundError: 当用户不存在时抛出
            ValidationError: 当邮箱已被其他用户使用时抛出
        """
        # 获取用户
        user = self.get_user_by_id(user_id)
        
        # 如果更新邮箱，检查是否已被使用
        if user_data.email and user_data.email != user.email:
            existing_user = self.repository.get_by_email(user_data.email)
            if existing_user:
                raise ValidationError(f"邮箱 {user_data.email} 已被使用")
        
        # 更新用户（只更新提供的字段）
        update_data = user_data.model_dump(exclude_unset=True)
        if update_data:
            try:
                updated_user = self.repository.update(user_id, update_data)
                self.db.commit()
                self.db.refresh(updated_user)
                return updated_user
            except IntegrityError as e:
                self.db.rollback()
                raise ValidationError(f"更新用户失败: {str(e)}")
        
        return user
    
    def delete_user(self, user_id: int) -> None:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Raises:
            NotFoundError: 当用户不存在时抛出
        """
        user = self.get_user_by_id(user_id)
        self.repository.delete(user_id)
        self.db.commit()
    
    def get_users(
        self,
        page: int = 1,
        page_size: int = 10,
        is_active: Optional[bool] = None
    ):
        """
        获取用户列表（分页）
        
        Args:
            page: 页码
            page_size: 每页数量
            is_active: 是否激活（可选，None 表示所有用户）
            
        Returns:
            PaginationResult[User]: 分页结果
        """
        if is_active is not None:
            return self.repository.paginate_active_users(page, page_size)
        else:
            return self.repository.paginate(page=page, page_size=page_size)
    
    def search_users(self, keyword: str, page: int = 1, page_size: int = 10):
        """
        搜索用户
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            PaginationResult[User]: 分页结果
        """
        return self.repository.search_users(keyword, page, page_size)

