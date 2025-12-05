"""
Repository 基础类模块

提供通用的 Repository 基类，包含基础的 CRUD 操作、分页查询和通用查询方法。
所有业务 Repository 都应继承自 BaseRepository。
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import IntegrityError

from app.db.base import BaseModel


# 定义泛型类型变量
ModelType = TypeVar("ModelType", bound=BaseModel)


class PaginationParams:
    """
    分页参数类
    
    用于封装分页查询的参数。
    """
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 10,
        max_page_size: int = 100
    ):
        """
        初始化分页参数
        
        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
            max_page_size: 最大每页数量（用于限制）
        """
        self.page = max(1, page)  # 确保页码至少为 1
        self.page_size = min(max(1, page_size), max_page_size)  # 确保在合理范围内
        self.max_page_size = max_page_size
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """获取限制数量"""
        return self.page_size


class PaginationResult(Generic[ModelType]):
    """
    分页结果类
    
    封装分页查询的结果，包含数据列表、总数、页码等信息。
    """
    
    def __init__(
        self,
        items: List[ModelType],
        total: int,
        page: int,
        page_size: int
    ):
        """
        初始化分页结果
        
        Args:
            items: 当前页的数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页数量
        """
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
    
    @property
    def total_pages(self) -> int:
        """计算总页数"""
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size
    
    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            dict: 包含分页信息和数据列表的字典
        """
        return {
            "items": [item.to_dict() if hasattr(item, "to_dict") else item for item in self.items],
            "pagination": {
                "total": self.total,
                "page": self.page,
                "page_size": self.page_size,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev,
            }
        }


class BaseRepository(Generic[ModelType]):
    """
    Repository 基础类
    
    提供通用的数据访问层（Repository Pattern）实现，包含：
    - 基础 CRUD 操作（Create, Read, Update, Delete）
    - 分页查询
    - 通用查询方法
    
    所有业务 Repository 都应继承此类，并指定对应的模型类型。
    
    示例：
        ```python
        from app.db.base import BaseModel
        from app.repositories.base import BaseRepository
        from sqlalchemy.orm import Session
        
        class User(BaseModel):
            __tablename__ = "users"
            name = Column(String(100), nullable=False)
        
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: Session):
                super().__init__(User, db)
        
        # 使用
        user_repo = UserRepository(db)
        user = user_repo.create({"name": "张三"})
        users = user_repo.get_all()
        ```
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        初始化 Repository
        
        Args:
            model: SQLAlchemy 模型类
            db: 数据库会话
        """
        self.model = model
        self.db = db
    
    # ==================== Create 操作 ====================
    
    def create(self, data: Dict[str, Any]) -> ModelType:
        """
        创建新记录
        
        Args:
            data: 包含字段数据的字典
            
        Returns:
            ModelType: 创建的模型实例
            
        Raises:
            IntegrityError: 当违反唯一性约束或其他完整性约束时抛出
            
        Example:
            ```python
            user = user_repo.create({"name": "张三", "email": "zhangsan@example.com"})
            ```
        """
        instance = self.model(**data)
        self.db.add(instance)
        try:
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except IntegrityError as e:
            self.db.rollback()
            raise e
    
    def create_many(self, data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        批量创建记录
        
        Args:
            data_list: 包含多个记录数据的字典列表
            
        Returns:
            List[ModelType]: 创建的模型实例列表
            
        Raises:
            IntegrityError: 当违反唯一性约束或其他完整性约束时抛出
            
        Example:
            ```python
            users = user_repo.create_many([
                {"name": "张三", "email": "zhangsan@example.com"},
                {"name": "李四", "email": "lisi@example.com"},
            ])
            ```
        """
        instances = [self.model(**data) for data in data_list]
        self.db.add_all(instances)
        try:
            self.db.commit()
            for instance in instances:
                self.db.refresh(instance)
            return instances
        except IntegrityError as e:
            self.db.rollback()
            raise e
    
    # ==================== Read 操作 ====================
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        根据 ID 获取记录
        
        Args:
            id: 记录 ID
            
        Returns:
            Optional[ModelType]: 找到的记录，如果不存在则返回 None
            
        Example:
            ```python
            user = user_repo.get_by_id(1)
            if user:
                print(user.name)
            ```
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: Optional[int] = None) -> List[ModelType]:
        """
        获取所有记录（支持分页）
        
        Args:
            skip: 跳过的记录数（用于分页）
            limit: 返回的最大记录数（用于分页）
            
        Returns:
            List[ModelType]: 记录列表
            
        Example:
            ```python
            # 获取所有记录
            users = user_repo.get_all()
            
            # 分页获取
            users = user_repo.get_all(skip=10, limit=20)
            ```
        """
        query = self.db.query(self.model)
        if skip > 0:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
        return query.all()
    
    def get_count(self) -> int:
        """
        获取记录总数
        
        Returns:
            int: 记录总数
            
        Example:
            ```python
            total = user_repo.get_count()
            ```
        """
        return self.db.query(self.model).count()
    
    def exists(self, id: int) -> bool:
        """
        检查记录是否存在
        
        Args:
            id: 记录 ID
            
        Returns:
            bool: 存在返回 True，否则返回 False
            
        Example:
            ```python
            if user_repo.exists(1):
                print("用户存在")
            ```
        """
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
    
    # ==================== Update 操作 ====================
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """
        更新记录
        
        Args:
            id: 记录 ID
            data: 包含要更新字段的字典
            
        Returns:
            Optional[ModelType]: 更新后的模型实例，如果记录不存在则返回 None
            
        Raises:
            IntegrityError: 当违反唯一性约束或其他完整性约束时抛出
            
        Example:
            ```python
            user = user_repo.update(1, {"name": "新名称"})
            if user:
                print(f"更新成功: {user.name}")
            ```
        """
        instance = self.get_by_id(id)
        if instance is None:
            return None
        
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except IntegrityError as e:
            self.db.rollback()
            raise e
    
    def update_or_create(
        self,
        filter_data: Dict[str, Any],
        update_data: Dict[str, Any],
        create_data: Optional[Dict[str, Any]] = None
    ) -> ModelType:
        """
        更新或创建记录
        
        如果记录存在（根据 filter_data 查找），则更新；否则创建新记录。
        
        Args:
            filter_data: 用于查找记录的过滤条件
            update_data: 更新数据
            create_data: 创建数据（如果不提供，则使用 update_data）
            
        Returns:
            ModelType: 更新或创建的模型实例
            
        Example:
            ```python
            # 如果邮箱为 "test@example.com" 的用户存在，则更新；否则创建
            user = user_repo.update_or_create(
                filter_data={"email": "test@example.com"},
                update_data={"name": "新名称"},
                create_data={"name": "新名称", "email": "test@example.com"}
            )
            ```
        """
        # 构建查询条件
        filters = [getattr(self.model, key) == value for key, value in filter_data.items()]
        instance = self.db.query(self.model).filter(and_(*filters)).first()
        
        if instance:
            # 更新现有记录
            for key, value in update_data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            try:
                self.db.commit()
                self.db.refresh(instance)
                return instance
            except IntegrityError as e:
                self.db.rollback()
                raise e
        else:
            # 创建新记录
            create_dict = create_data if create_data is not None else {**filter_data, **update_data}
            return self.create(create_dict)
    
    # ==================== Delete 操作 ====================
    
    def delete(self, id: int) -> bool:
        """
        删除记录
        
        Args:
            id: 记录 ID
            
        Returns:
            bool: 删除成功返回 True，记录不存在返回 False
            
        Example:
            ```python
            if user_repo.delete(1):
                print("删除成功")
            ```
        """
        instance = self.get_by_id(id)
        if instance is None:
            return False
        
        self.db.delete(instance)
        self.db.commit()
        return True
    
    def delete_many(self, ids: List[int]) -> int:
        """
        批量删除记录
        
        Args:
            ids: 要删除的记录 ID 列表
            
        Returns:
            int: 实际删除的记录数
            
        Example:
            ```python
            deleted_count = user_repo.delete_many([1, 2, 3])
            print(f"删除了 {deleted_count} 条记录")
            ```
        """
        deleted_count = self.db.query(self.model).filter(self.model.id.in_(ids)).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count
    
    def delete_all(self) -> int:
        """
        删除所有记录
        
        警告：此操作会删除表中的所有数据，请谨慎使用！
        
        Returns:
            int: 删除的记录数
            
        Example:
            ```python
            deleted_count = user_repo.delete_all()
            print(f"删除了 {deleted_count} 条记录")
            ```
        """
        deleted_count = self.db.query(self.model).delete()
        self.db.commit()
        return deleted_count
    
    # ==================== 分页查询 ====================
    
    def paginate(
        self,
        page: int = 1,
        page_size: int = 10,
        max_page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> PaginationResult[ModelType]:
        """
        分页查询
        
        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
            max_page_size: 最大每页数量
            order_by: 排序字段名（可选）
            order_desc: 是否降序排列（默认 False，即升序）
            
        Returns:
            PaginationResult[ModelType]: 分页结果对象
            
        Example:
            ```python
            # 基本分页
            result = user_repo.paginate(page=1, page_size=10)
            print(f"总数: {result.total}, 当前页: {result.page}")
            for user in result.items:
                print(user.name)
            
            # 带排序的分页
            result = user_repo.paginate(
                page=1,
                page_size=10,
                order_by="created_at",
                order_desc=True
            )
            ```
        """
        pagination = PaginationParams(page=page, page_size=page_size, max_page_size=max_page_size)
        
        # 构建查询
        query = self.db.query(self.model)
        
        # 排序
        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        items = query.offset(pagination.offset).limit(pagination.limit).all()
        
        return PaginationResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
    
    # ==================== 通用查询方法 ====================
    
    def filter_by(self, **filters) -> List[ModelType]:
        """
        根据条件过滤查询
        
        Args:
            **filters: 过滤条件（字段名=值）
            
        Returns:
            List[ModelType]: 符合条件的记录列表
            
        Example:
            ```python
            # 查询 name 为 "张三" 的用户
            users = user_repo.filter_by(name="张三")
            
            # 多条件查询
            users = user_repo.filter_by(name="张三", email="zhangsan@example.com")
            ```
        """
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def filter_one(self, **filters) -> Optional[ModelType]:
        """
        根据条件查询单条记录
        
        Args:
            **filters: 过滤条件（字段名=值）
            
        Returns:
            Optional[ModelType]: 找到的记录，如果不存在则返回 None
            
        Example:
            ```python
            user = user_repo.filter_one(email="zhangsan@example.com")
            if user:
                print(user.name)
            ```
        """
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first()
    
    def filter_by_dict(self, filters: Dict[str, Any]) -> List[ModelType]:
        """
        根据字典条件过滤查询
        
        Args:
            filters: 包含过滤条件的字典
            
        Returns:
            List[ModelType]: 符合条件的记录列表
            
        Example:
            ```python
            users = user_repo.filter_by_dict({"name": "张三", "email": "zhangsan@example.com"})
            ```
        """
        return self.filter_by(**filters)
    
    def search(
        self,
        search_fields: List[str],
        keyword: str,
        skip: int = 0,
        limit: Optional[int] = None
    ) -> List[ModelType]:
        """
        关键字搜索（模糊匹配）
        
        在指定的多个字段中搜索包含关键字的记录。
        
        Args:
            search_fields: 要搜索的字段名列表
            keyword: 搜索关键字
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            List[ModelType]: 符合条件的记录列表
            
        Example:
            ```python
            # 在 name 和 email 字段中搜索 "张"
            users = user_repo.search(["name", "email"], "张")
            ```
        """
        if not keyword or not search_fields:
            return []
        
        query = self.db.query(self.model)
        
        # 构建 OR 条件：任一字段包含关键字
        conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                # 使用 LIKE 进行模糊匹配
                conditions.append(column.like(f"%{keyword}%"))
        
        if conditions:
            query = query.filter(or_(*conditions))
        
        if skip > 0:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
        
        return query.all()
    
    def query_builder(self):
        """
        获取查询构建器
        
        返回 SQLAlchemy Query 对象，用于构建复杂的自定义查询。
        
        Returns:
            Query: SQLAlchemy Query 对象
            
        Example:
            ```python
            # 使用查询构建器进行复杂查询
            query = user_repo.query_builder()
            users = query.filter(
                User.age >= 18,
                User.status == "active"
            ).order_by(User.created_at.desc()).all()
            ```
        """
        return self.db.query(self.model)

