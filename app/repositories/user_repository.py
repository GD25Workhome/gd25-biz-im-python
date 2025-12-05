"""
用户 Repository 示例

展示如何继承 BaseRepository 创建业务 Repository。
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User
from app.repositories.base import BaseRepository, PaginationParams, PaginationResult


class UserRepository(BaseRepository[User]):
    """
    用户 Repository
    
    继承自 BaseRepository，自动获得基础的 CRUD 操作。
    可以添加用户特定的查询方法。
    
    示例：
        ```python
        from app.repositories.user_repository import UserRepository
        from app.db.session import get_db
        
        db = next(get_db())
        repo = UserRepository(db)
        
        # 创建用户
        user = repo.create({"name": "张三", "email": "zhangsan@example.com"})
        
        # 根据邮箱查询
        user = repo.get_by_email("zhangsan@example.com")
        
        # 分页查询
        result = repo.paginate_active_users(page=1, page_size=10)
        ```
    """
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            Optional[User]: 用户对象，如果不存在返回 None
        """
        return self.filter_one(User.email == email)
    
    def get_active_users(self) -> list[User]:
        """
        获取所有激活的用户
        
        Returns:
            list[User]: 激活用户列表
        """
        return self.filter_by(is_active=True)
    
    def paginate_active_users(
        self,
        page: int = 1,
        page_size: int = 10,
        order_by: Optional[str] = None
    ) -> PaginationResult[User]:
        """
        分页查询激活用户
        
        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
            order_by: 排序字段（可选，默认按创建时间倒序）
            
        Returns:
            PaginationResult[User]: 分页结果
        """
        params = PaginationParams(page=page, page_size=page_size)
        
        # 默认按创建时间倒序
        if order_by is None:
            order_by = "-created_at"
        
        return self.paginate(
            filters={"is_active": True},
            page=params.page,
            page_size=params.page_size,
            order_by=order_by
        )
    
    def search_users(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 10
    ) -> PaginationResult[User]:
        """
        搜索用户（根据姓名或邮箱）
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            PaginationResult[User]: 分页结果
        """
        params = PaginationParams(page=page, page_size=page_size)
        
        # 在姓名和邮箱字段中搜索
        return self.search(
            keyword=keyword,
            fields=["name", "email"],
            page=params.page,
            page_size=params.page_size
        )

