"""
Repository 基础类测试模块

测试 Repository 基础类的所有功能，包括：
- CRUD 操作（Create, Read, Update, Delete）
- 分页查询
- 通用查询方法
- 批量操作
- 异常处理
"""

import sys
from pathlib import Path
from typing import Optional

import pytest
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.base import BaseModel
from app.db.database import get_engine, close_engine
from app.db.session import SessionLocal, get_db_session
from app.repositories.base import (
    BaseRepository,
    PaginationParams,
    PaginationResult,
)


# ==================== 测试模型 ====================

class UserModel(BaseModel):
    """测试用户模型"""
    __tablename__ = "test_users"
    
    name = Column(String(100), nullable=False, comment="用户名")
    email = Column(String(255), unique=True, nullable=False, comment="邮箱")
    age = Column(Integer, nullable=True, comment="年龄")
    is_active = Column(Boolean, default=True, comment="是否激活")


class UserRepository(BaseRepository[UserModel]):
    """测试用户 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(UserModel, db)


# ==================== 测试 Fixtures ====================

@pytest.fixture(scope="function")
def db_session():
    """
    创建测试数据库会话
    
    每个测试函数都会创建一个新的会话，测试结束后自动回滚。
    """
    # 创建表
    engine = get_engine()
    BaseModel.metadata.create_all(bind=engine)
    
    # 创建会话
    db = SessionLocal()
    
    try:
        yield db
    finally:
        # 回滚所有更改
        db.rollback()
        # 关闭会话
        db.close()
        # 删除表
        BaseModel.metadata.drop_all(bind=engine)


@pytest.fixture
def repository(db_session: Session) -> UserRepository:
    """创建测试 Repository 实例"""
    return UserRepository(db_session)


# ==================== Create 操作测试 ====================

def test_create(repository: UserRepository):
    """测试创建单条记录"""
    user_data = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25,
        "is_active": True
    }
    
    user = repository.create(user_data)
    
    assert user is not None
    assert user.id is not None
    assert user.name == "张三"
    assert user.email == "zhangsan@example.com"
    assert user.age == 25
    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None


def test_create_many(repository: UserRepository):
    """测试批量创建记录"""
    users_data = [
        {"name": "张三", "email": "zhangsan@example.com", "age": 25},
        {"name": "李四", "email": "lisi@example.com", "age": 30},
        {"name": "王五", "email": "wangwu@example.com", "age": 28},
    ]
    
    users = repository.create_many(users_data)
    
    assert len(users) == 3
    assert all(user.id is not None for user in users)
    assert users[0].name == "张三"
    assert users[1].name == "李四"
    assert users[2].name == "王五"


def test_create_with_unique_constraint(repository: UserRepository):
    """测试创建时违反唯一性约束"""
    user_data = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25
    }
    
    # 创建第一条记录
    repository.create(user_data)
    
    # 尝试创建相同邮箱的记录（应该失败）
    with pytest.raises(IntegrityError):
        repository.create(user_data)


# ==================== Read 操作测试 ====================

def test_get_by_id(repository: UserRepository):
    """测试根据 ID 获取记录"""
    # 创建测试数据
    user = repository.create({
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25
    })
    
    # 根据 ID 获取
    found_user = repository.get_by_id(user.id)
    
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.name == "张三"
    assert found_user.email == "zhangsan@example.com"


def test_get_by_id_not_found(repository: UserRepository):
    """测试根据不存在的 ID 获取记录"""
    user = repository.get_by_id(99999)
    assert user is None


def test_get_all(repository: UserRepository):
    """测试获取所有记录"""
    # 创建多条测试数据
    repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25})
    repository.create({"name": "李四", "email": "lisi@example.com", "age": 30})
    repository.create({"name": "王五", "email": "wangwu@example.com", "age": 28})
    
    # 获取所有记录
    users = repository.get_all()
    
    assert len(users) == 3
    assert all(user.id is not None for user in users)


def test_get_all_with_pagination(repository: UserRepository):
    """测试分页获取记录"""
    # 创建多条测试数据
    for i in range(10):
        repository.create({
            "name": f"用户{i}",
            "email": f"user{i}@example.com",
            "age": 20 + i
        })
    
    # 获取前 5 条
    users = repository.get_all(skip=0, limit=5)
    assert len(users) == 5
    
    # 获取第 6-10 条
    users = repository.get_all(skip=5, limit=5)
    assert len(users) == 5


def test_get_count(repository: UserRepository):
    """测试获取记录总数"""
    # 初始数量应该为 0
    assert repository.get_count() == 0
    
    # 创建几条记录
    repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25})
    repository.create({"name": "李四", "email": "lisi@example.com", "age": 30})
    
    # 数量应该为 2
    assert repository.get_count() == 2


def test_exists(repository: UserRepository):
    """测试检查记录是否存在"""
    # 创建测试数据
    user = repository.create({
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25
    })
    
    # 应该存在
    assert repository.exists(user.id) is True
    
    # 不存在的 ID
    assert repository.exists(99999) is False


# ==================== Update 操作测试 ====================

def test_update(repository: UserRepository):
    """测试更新记录"""
    # 创建测试数据
    user = repository.create({
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25
    })
    
    original_updated_at = user.updated_at
    
    # 更新记录
    updated_user = repository.update(user.id, {"name": "李四", "age": 30})
    
    assert updated_user is not None
    assert updated_user.id == user.id
    assert updated_user.name == "李四"
    assert updated_user.age == 30
    assert updated_user.email == "zhangsan@example.com"  # 未更新的字段保持不变
    # 注意：updated_at 可能会更新，但取决于数据库配置


def test_update_not_found(repository: UserRepository):
    """测试更新不存在的记录"""
    updated_user = repository.update(99999, {"name": "新名称"})
    assert updated_user is None


def test_update_or_create_create(repository: UserRepository):
    """测试更新或创建 - 创建新记录"""
    # 记录不存在，应该创建
    user = repository.update_or_create(
        filter_data={"email": "zhangsan@example.com"},
        update_data={"name": "张三"},
        create_data={"name": "张三", "email": "zhangsan@example.com", "age": 25}
    )
    
    assert user is not None
    assert user.id is not None
    assert user.name == "张三"
    assert user.email == "zhangsan@example.com"
    assert user.age == 25


def test_update_or_create_update(repository: UserRepository):
    """测试更新或创建 - 更新现有记录"""
    # 先创建一条记录
    user = repository.create({
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25
    })
    
    # 记录存在，应该更新
    updated_user = repository.update_or_create(
        filter_data={"email": "zhangsan@example.com"},
        update_data={"name": "李四", "age": 30}
    )
    
    assert updated_user is not None
    assert updated_user.id == user.id
    assert updated_user.name == "李四"
    assert updated_user.age == 30
    assert updated_user.email == "zhangsan@example.com"


# ==================== Delete 操作测试 ====================

def test_delete(repository: UserRepository):
    """测试删除记录"""
    # 创建测试数据
    user = repository.create({
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25
    })
    
    user_id = user.id
    
    # 删除记录
    result = repository.delete(user_id)
    
    assert result is True
    # 验证记录已被删除
    assert repository.get_by_id(user_id) is None


def test_delete_not_found(repository: UserRepository):
    """测试删除不存在的记录"""
    result = repository.delete(99999)
    assert result is False


def test_delete_many(repository: UserRepository):
    """测试批量删除记录"""
    # 创建多条测试数据
    user1 = repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25})
    user2 = repository.create({"name": "李四", "email": "lisi@example.com", "age": 30})
    user3 = repository.create({"name": "王五", "email": "wangwu@example.com", "age": 28})
    
    # 保存 ID（在删除之前）
    user1_id = user1.id
    user2_id = user2.id
    user3_id = user3.id
    
    # 批量删除
    deleted_count = repository.delete_many([user1_id, user2_id])
    
    assert deleted_count == 2
    # 验证记录已被删除
    assert repository.get_by_id(user1_id) is None
    assert repository.get_by_id(user2_id) is None
    # 第三条记录应该还在
    assert repository.get_by_id(user3_id) is not None


def test_delete_all(repository: UserRepository):
    """测试删除所有记录"""
    # 创建多条测试数据
    repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25})
    repository.create({"name": "李四", "email": "lisi@example.com", "age": 30})
    repository.create({"name": "王五", "email": "wangwu@example.com", "age": 28})
    
    # 删除所有记录
    deleted_count = repository.delete_all()
    
    assert deleted_count == 3
    # 验证所有记录已被删除
    assert repository.get_count() == 0


# ==================== 分页查询测试 ====================

def test_paginate_basic(repository: UserRepository):
    """测试基本分页查询"""
    # 创建多条测试数据
    for i in range(15):
        repository.create({
            "name": f"用户{i}",
            "email": f"user{i}@example.com",
            "age": 20 + i
        })
    
    # 第一页，每页 10 条
    result = repository.paginate(page=1, page_size=10)
    
    assert result.total == 15
    assert result.page == 1
    assert result.page_size == 10
    assert len(result.items) == 10
    assert result.total_pages == 2
    assert result.has_next is True
    assert result.has_prev is False


def test_paginate_second_page(repository: UserRepository):
    """测试第二页分页查询"""
    # 创建多条测试数据
    for i in range(15):
        repository.create({
            "name": f"用户{i}",
            "email": f"user{i}@example.com",
            "age": 20 + i
        })
    
    # 第二页，每页 10 条
    result = repository.paginate(page=2, page_size=10)
    
    assert result.total == 15
    assert result.page == 2
    assert result.page_size == 10
    assert len(result.items) == 5  # 第二页只有 5 条
    assert result.total_pages == 2
    assert result.has_next is False
    assert result.has_prev is True


def test_paginate_with_order(repository: UserRepository):
    """测试带排序的分页查询"""
    # 创建多条测试数据
    for i in range(5):
        repository.create({
            "name": f"用户{i}",
            "email": f"user{i}@example.com",
            "age": 20 + i
        })
    
    # 按年龄降序排列
    result = repository.paginate(
        page=1,
        page_size=10,
        order_by="age",
        order_desc=True
    )
    
    assert len(result.items) == 5
    # 验证排序（年龄应该是降序）
    ages = [user.age for user in result.items]
    assert ages == sorted(ages, reverse=True)


def test_paginate_empty(repository: UserRepository):
    """测试空结果的分页查询"""
    result = repository.paginate(page=1, page_size=10)
    
    assert result.total == 0
    assert result.page == 1
    assert result.page_size == 10
    assert len(result.items) == 0
    assert result.total_pages == 0
    assert result.has_next is False
    assert result.has_prev is False


def test_paginate_to_dict(repository: UserRepository):
    """测试分页结果转换为字典"""
    # 创建测试数据
    repository.create({
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25
    })
    
    result = repository.paginate(page=1, page_size=10)
    data = result.to_dict()
    
    assert "items" in data
    assert "pagination" in data
    assert len(data["items"]) == 1
    assert data["pagination"]["total"] == 1
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 10
    assert data["pagination"]["total_pages"] == 1
    assert data["pagination"]["has_next"] is False
    assert data["pagination"]["has_prev"] is False


# ==================== 通用查询测试 ====================

def test_filter_by(repository: UserRepository):
    """测试条件过滤查询"""
    # 创建测试数据
    repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25, "is_active": True})
    repository.create({"name": "李四", "email": "lisi@example.com", "age": 30, "is_active": True})
    repository.create({"name": "王五", "email": "wangwu@example.com", "age": 28, "is_active": False})
    
    # 单条件过滤
    users = repository.filter_by(name="张三")
    assert len(users) == 1
    assert users[0].name == "张三"
    
    # 多条件过滤
    users = repository.filter_by(is_active=True)
    assert len(users) == 2


def test_filter_one(repository: UserRepository):
    """测试单条记录查询"""
    # 创建测试数据
    repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25})
    
    # 查询单条记录
    user = repository.filter_one(email="zhangsan@example.com")
    
    assert user is not None
    assert user.name == "张三"
    assert user.email == "zhangsan@example.com"


def test_filter_one_not_found(repository: UserRepository):
    """测试查询不存在的单条记录"""
    user = repository.filter_one(email="notfound@example.com")
    assert user is None


def test_filter_by_dict(repository: UserRepository):
    """测试字典条件过滤"""
    # 创建测试数据
    repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25, "is_active": True})
    
    # 使用字典过滤
    users = repository.filter_by_dict({"name": "张三", "is_active": True})
    
    assert len(users) == 1
    assert users[0].name == "张三"


def test_search(repository: UserRepository):
    """测试关键字搜索"""
    # 创建测试数据
    repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25})
    repository.create({"name": "李四", "email": "lisi@example.com", "age": 30})
    repository.create({"name": "张五", "email": "zhangwu@example.com", "age": 28})
    
    # 在 name 和 email 字段中搜索 "张"
    users = repository.search(["name", "email"], "张")
    
    assert len(users) == 2
    assert all("张" in user.name or "张" in user.email for user in users)


def test_search_empty_keyword(repository: UserRepository):
    """测试空关键字搜索"""
    repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25})
    
    # 空关键字应该返回空列表
    users = repository.search(["name", "email"], "")
    assert len(users) == 0


def test_search_with_pagination(repository: UserRepository):
    """测试带分页的关键字搜索"""
    # 创建多条测试数据
    for i in range(10):
        repository.create({
            "name": f"用户{i}",
            "email": f"user{i}@example.com",
            "age": 20 + i
        })
    
    # 搜索并分页
    users = repository.search(["name", "email"], "用户", skip=0, limit=5)
    
    assert len(users) <= 5


def test_query_builder(repository: UserRepository):
    """测试查询构建器"""
    # 创建测试数据
    repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25})
    repository.create({"name": "李四", "email": "lisi@example.com", "age": 30})
    repository.create({"name": "王五", "email": "wangwu@example.com", "age": 28})
    
    # 使用查询构建器进行复杂查询
    query = repository.query_builder()
    users = query.filter(UserModel.age >= 25, UserModel.age <= 30).all()
    
    assert len(users) == 3
    assert all(25 <= user.age <= 30 for user in users)


# ==================== PaginationParams 测试 ====================

def test_pagination_params():
    """测试分页参数类"""
    # 基本参数
    params = PaginationParams(page=1, page_size=10)
    assert params.page == 1
    assert params.page_size == 10
    assert params.offset == 0
    assert params.limit == 10
    
    # 第二页
    params = PaginationParams(page=2, page_size=10)
    assert params.page == 2
    assert params.offset == 10
    assert params.limit == 10
    
    # 边界情况：页码小于 1
    params = PaginationParams(page=0, page_size=10)
    assert params.page == 1  # 应该自动调整为 1
    
    # 边界情况：每页数量超过最大值
    params = PaginationParams(page=1, page_size=200, max_page_size=100)
    assert params.page_size == 100  # 应该被限制为最大值


# ==================== PaginationResult 测试 ====================

def test_pagination_result(db_session: Session):
    """测试分页结果类"""
    # 创建实际的测试数据
    repository = UserRepository(db_session)
    for i in range(1, 6):
        repository.create({
            "name": f"用户{i}",
            "email": f"user{i}@example.com",
            "age": 20 + i
        })
    
    # 创建分页结果
    result = repository.paginate(page=1, page_size=5)
    
    assert len(result.items) == 5
    assert result.total == 5
    assert result.page == 1
    assert result.page_size == 5
    assert result.total_pages == 1
    assert result.has_next is False
    assert result.has_prev is False


def test_pagination_result_last_page(db_session: Session):
    """测试最后一页的分页结果"""
    repository = UserRepository(db_session)
    # 创建 20 条记录
    for i in range(20):
        repository.create({
            "name": f"用户{i}",
            "email": f"user{i}@example.com",
            "age": 20 + i
        })
    
    # 获取最后一页（第 4 页，每页 5 条）
    result = repository.paginate(page=4, page_size=5)
    
    assert result.total == 20
    assert result.total_pages == 4
    assert result.has_next is False
    assert result.has_prev is True
    assert len(result.items) == 5  # 最后一页有 5 条记录


# ==================== 集成测试 ====================

def test_repository_full_workflow(repository: UserRepository):
    """测试 Repository 完整工作流程"""
    # 1. 创建多条记录
    user1 = repository.create({"name": "张三", "email": "zhangsan@example.com", "age": 25})
    user2 = repository.create({"name": "李四", "email": "lisi@example.com", "age": 30})
    
    # 2. 查询记录
    found_user = repository.get_by_id(user1.id)
    assert found_user is not None
    assert found_user.name == "张三"
    
    # 3. 更新记录（只更新 name，age 保持不变）
    updated_user = repository.update(user1.id, {"name": "张三更新"})
    assert updated_user is not None
    assert updated_user.name == "张三更新"
    assert updated_user.age == 25  # age 应该保持不变
    
    # 4. 分页查询
    result = repository.paginate(page=1, page_size=10)
    assert result.total == 2
    
    # 5. 条件查询（查询 age=25 的记录，应该还有一条，因为只更新了 name）
    users = repository.filter_by(age=25)
    assert len(users) == 1  # 更新后 age 仍然是 25
    
    # 6. 删除记录
    assert repository.delete(user1.id) is True
    assert repository.get_count() == 1


# ==================== 运行所有测试 ====================

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试 Repository 基础类")
    print("=" * 60)
    
    try:
        # 注意：这里只是示例，实际应该使用 pytest 运行
        print("请使用 pytest 运行测试：")
        print("  pytest tests/test_repository.py -v")
        print("\n所有测试用例已准备就绪！")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_tests()

