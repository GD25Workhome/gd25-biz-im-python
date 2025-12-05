"""
Pytest 配置和共享 Fixture

提供所有测试文件共享的 fixture 和配置，包括：
- 测试数据库配置
- 数据库会话 fixture
- 测试客户端 fixture
- 其他通用测试工具
"""

import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.main import app
from app.db.base import Base, BaseModel
from app.config import settings


# ==================== 测试数据库配置 ====================

# 使用 SQLite 内存数据库进行测试（快速、隔离）
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """
    创建测试数据库引擎（会话级别）
    
    使用 SQLite 内存数据库，所有测试共享同一个引擎。
    测试会话结束后自动清理。
    """
    # 创建测试引擎（使用内存数据库）
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite 需要此参数
        poolclass=StaticPool,  # 使用静态连接池
        echo=False,  # 测试时不打印 SQL
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # 清理：删除所有表
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    创建测试数据库会话（函数级别）
    
    每个测试函数都会创建一个新的会话，测试结束后自动回滚。
    这样可以确保测试之间的数据隔离。
    
    Yields:
        Session: 数据库会话实例
    """
    # 创建会话工厂
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    
    # 创建会话
    db = TestingSessionLocal()
    
    try:
        # 测试前：可以在这里插入测试数据
        yield db
    finally:
        # 测试后：回滚所有更改，确保数据隔离
        db.rollback()
        db.close()


# ==================== 测试客户端 Fixture ====================

@pytest.fixture
def client() -> TestClient:
    """
    创建 FastAPI 测试客户端
    
    用于测试 API 端点，自动处理请求和响应。
    
    Returns:
        TestClient: FastAPI 测试客户端实例
    """
    return TestClient(app)


@pytest.fixture
def authenticated_client(client: TestClient) -> TestClient:
    """
    创建已认证的测试客户端（示例）
    
    如果需要测试需要认证的接口，可以在这里添加认证逻辑。
    目前返回普通客户端，实际使用时需要根据项目的认证方式实现。
    
    Args:
        client: 基础测试客户端
        
    Returns:
        TestClient: 已认证的测试客户端
    """
    # TODO: 根据项目的认证方式实现
    # 示例：添加认证 token
    # client.headers.update({"Authorization": f"Bearer {token}"})
    return client


# ==================== 测试数据 Fixture ====================

@pytest.fixture
def sample_user_data() -> dict:
    """
    示例用户数据
    
    用于测试用户相关的功能。
    
    Returns:
        dict: 用户数据字典
    """
    return {
        "name": "测试用户",
        "email": "test@example.com",
        "age": 25,
        "is_active": True,
    }


@pytest.fixture
def sample_users_data() -> list[dict]:
    """
    示例用户列表数据
    
    用于测试批量操作。
    
    Returns:
        list[dict]: 用户数据列表
    """
    return [
        {"name": "用户1", "email": "user1@example.com", "age": 20},
        {"name": "用户2", "email": "user2@example.com", "age": 25},
        {"name": "用户3", "email": "user3@example.com", "age": 30},
    ]


# ==================== 配置 Mock Fixture ====================

@pytest.fixture
def mock_settings():
    """
    Mock 配置对象
    
    用于测试时覆盖配置项，避免依赖实际的环境变量。
    
    Returns:
        MagicMock: Mock 配置对象
    """
    from unittest.mock import MagicMock
    
    mock = MagicMock()
    mock.app_name = "test-app"
    mock.app_version = "1.0.0"
    mock.debug = True
    mock.environment = "testing"
    mock.database_url = TEST_DATABASE_URL
    mock.cors_origins = ["http://localhost:3000"]
    mock.log_level = "DEBUG"
    mock.log_format = "text"
    
    return mock


# ==================== 数据库操作辅助函数 ====================

def cleanup_database(db: Session) -> None:
    """
    清理数据库（辅助函数）
    
    删除所有测试数据，确保测试环境干净。
    
    Args:
        db: 数据库会话
    """
    # 获取所有表
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(text(f"DELETE FROM {table.name}"))
    db.commit()


def reset_database(db: Session) -> None:
    """
    重置数据库（辅助函数）
    
    删除所有表并重新创建，用于需要完全重置的场景。
    
    Args:
        db: 数据库会话
    """
    Base.metadata.drop_all(bind=db.bind)
    Base.metadata.create_all(bind=db.bind)
    db.commit()


# ==================== Pytest 配置 ====================

# 配置 pytest 标记
def pytest_configure(config):
    """配置 pytest 标记"""
    config.addinivalue_line(
        "markers", "unit: 单元测试（不依赖外部资源）"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试（依赖数据库等外部资源）"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试（执行时间较长）"
    )
    config.addinivalue_line(
        "markers", "requires_db: 需要数据库的测试"
    )


# ==================== 测试钩子 ====================

@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    自动执行的测试环境设置
    
    每个测试函数执行前自动运行，用于设置测试环境。
    """
    # 测试前的设置
    yield
    # 测试后的清理（如果需要）

