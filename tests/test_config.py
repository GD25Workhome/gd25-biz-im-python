"""
配置管理测试模块

测试配置管理模块的所有功能，包括：
- 配置加载和验证
- 环境变量读取
- 配置扩展
- 配置验证规则
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import Settings, settings


# ==================== 配置加载测试 ====================

def test_config_loading():
    """测试配置加载"""
    # 测试必需配置项
    assert settings.app_name is not None
    assert settings.app_version is not None
    assert settings.environment is not None
    
    # 测试可选配置项（如果未配置，可能为 None）
    print(f"App name: {settings.app_name}")
    print(f"App version: {settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Database URL: {settings.database_url}")  # 可能为 None
    print(f"CORS origins: {settings.cors_origins}")  # 应该有默认值


def test_config_default_values():
    """测试配置默认值"""
    # 测试默认值
    assert settings.app_name == "gd25-arch-backend"
    assert settings.app_version == "1.0.0"
    assert settings.environment == "development"
    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert settings.log_format == "json"


def test_config_environment_validation():
    """测试环境值验证"""
    # 测试有效环境值
    valid_environments = ["development", "testing", "production"]
    for env in valid_environments:
        with patch.dict("os.environ", {"ENVIRONMENT": env}):
            config = Settings()
            assert config.environment == env
    
    # 测试无效环境值
    with patch.dict("os.environ", {"ENVIRONMENT": "invalid"}):
        with pytest.raises(ValueError, match="environment 必须是"):
            Settings()


def test_config_log_level_validation():
    """测试日志级别验证"""
    # 测试有效日志级别
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    for level in valid_levels:
        with patch.dict("os.environ", {"LOG_LEVEL": level}):
            config = Settings()
            assert config.log_level == level
    
    # 测试无效日志级别
    with patch.dict("os.environ", {"LOG_LEVEL": "INVALID"}):
        with pytest.raises(ValueError, match="log_level 必须是"):
            Settings()


def test_config_log_format_validation():
    """测试日志格式验证"""
    # 测试有效格式
    valid_formats = ["json", "text"]
    for fmt in valid_formats:
        with patch.dict("os.environ", {"LOG_FORMAT": fmt}):
            config = Settings()
            assert config.log_format == fmt
    
    # 测试无效格式
    with patch.dict("os.environ", {"LOG_FORMAT": "invalid"}):
        with pytest.raises(ValueError, match="log_format 必须是"):
            Settings()


def test_config_database_url_validation():
    """测试数据库 URL 验证"""
    # 测试有效的 PostgreSQL URL
    with patch.dict("os.environ", {"DATABASE_URL": "postgresql://user:pass@localhost:5432/db"}):
        config = Settings()
        assert config.database_url.startswith("postgresql://")
    
    # 测试有效的 MySQL URL
    with patch.dict("os.environ", {"DATABASE_URL": "mysql+pymysql://user:pass@localhost:3306/db"}):
        config = Settings()
        assert config.database_url.startswith("mysql+pymysql://")
    
    # 测试无效的数据库 URL
    with patch.dict("os.environ", {"DATABASE_URL": "invalid://url"}):
        with pytest.raises(ValueError, match="database_url 必须以"):
            Settings()


def test_config_cors_origins():
    """测试 CORS 源配置"""
    # 测试默认值
    assert len(settings.cors_origins) > 0
    assert "http://localhost:3000" in settings.cors_origins
    
    # 测试自定义配置（字符串格式）
    with patch.dict("os.environ", {"CORS_ORIGINS": "http://localhost:3000,http://localhost:8080"}):
        config = Settings()
        assert len(config.cors_origins) == 2
        assert "http://localhost:3000" in config.cors_origins
        assert "http://localhost:8080" in config.cors_origins


def test_config_environment_methods():
    """测试环境判断方法"""
    # 测试开发环境
    with patch.dict("os.environ", {"ENVIRONMENT": "development"}):
        config = Settings()
        assert config.is_development() is True
        assert config.is_testing() is False
        assert config.is_production() is False
    
    # 测试测试环境
    with patch.dict("os.environ", {"ENVIRONMENT": "testing"}):
        config = Settings()
        assert config.is_development() is False
        assert config.is_testing() is True
        assert config.is_production() is False
    
    # 测试生产环境
    with patch.dict("os.environ", {"ENVIRONMENT": "production"}):
        config = Settings()
        assert config.is_development() is False
        assert config.is_testing() is False
        assert config.is_production() is True


def test_config_extension():
    """测试配置扩展"""
    # 测试继承 Settings 类添加自定义配置
    class CustomSettings(Settings):
        """自定义配置"""
        custom_key: str = "custom_value"
        max_retries: int = 3
    
    custom_config = CustomSettings()
    assert custom_config.custom_key == "custom_value"
    assert custom_config.max_retries == 3
    assert custom_config.app_name == "gd25-arch-backend"  # 继承的配置


def test_config_database_url_methods():
    """测试数据库 URL 方法"""
    # 测试同步 URL
    with patch.dict("os.environ", {"DATABASE_URL": "postgresql://user:pass@localhost:5432/db"}):
        config = Settings()
        sync_url = config.get_database_url_sync()
        assert sync_url == "postgresql://user:pass@localhost:5432/db"
    
    # 测试异步 URL（PostgreSQL）
    with patch.dict("os.environ", {"DATABASE_URL": "postgresql://user:pass@localhost:5432/db"}):
        config = Settings()
        async_url = config.get_database_url_async()
        assert async_url == "postgresql+asyncpg://user:pass@localhost:5432/db"
    
    # 测试异步 URL（MySQL）
    with patch.dict("os.environ", {"DATABASE_URL": "mysql+pymysql://user:pass@localhost:3306/db"}):
        config = Settings()
        async_url = config.get_database_url_async()
        assert async_url == "mysql+aiomysql://user:pass@localhost:3306/db"
    
    # 测试未配置时抛出异常
    with patch.dict("os.environ", {}, clear=True):
        config = Settings()
        with pytest.raises(ValueError, match="database_url 未配置"):
            config.get_database_url_sync()

