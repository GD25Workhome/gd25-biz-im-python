"""
配置管理模块

使用 Pydantic Settings 进行配置验证和管理，支持环境变量读取和 .env 文件加载。
提供配置扩展机制，允许项目添加自定义配置项。
"""

from typing import List, Optional, Any, Dict, Annotated, Union
from pydantic import Field, field_validator, BeforeValidator, model_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_cors_origins(v: Any) -> List[str]:
    """
    解析 CORS 源列表
    
    支持多种格式：
    - 字符串（逗号分隔）："http://localhost:3000,http://localhost:8080"
    - 列表：["http://localhost:3000", "http://localhost:8080"]
    - 空值：返回默认值
    """
    if v is None:
        return ["http://localhost:3000", "http://localhost:8080"]
    if isinstance(v, str):
        # 处理空字符串
        if not v.strip():
            return ["http://localhost:3000", "http://localhost:8080"]
        # 从字符串解析，支持逗号分隔
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    elif isinstance(v, list):
        return v
    else:
        return ["http://localhost:3000", "http://localhost:8080"]


class Settings(BaseSettings):
    """
    应用配置类
    
    使用 Pydantic Settings 进行配置验证，支持从环境变量和 .env 文件加载配置。
    所有配置项都可以通过环境变量设置，环境变量名使用大写字母和下划线。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 允许额外的配置项，用于扩展
    )

    # ==================== 应用配置 ====================
    app_name: str = Field(
        default="gd25-arch-backend",
        description="应用名称",
    )
    app_version: str = Field(
        default="1.0.0",
        description="应用版本",
    )
    debug: bool = Field(
        default=False,
        description="调试模式",
    )
    environment: str = Field(
        default="development",
        description="运行环境：development, testing, production",
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证环境值"""
        allowed = ["development", "testing", "production"]
        if v not in allowed:
            raise ValueError(f"environment 必须是 {allowed} 之一")
        return v

    # ==================== 数据库配置 ====================
    database_url: Optional[str] = Field(
        default=None,
        description="数据库连接 URL，格式：postgresql://user:password@host:port/dbname 或 mysql+pymysql://user:password@host:port/dbname",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        """验证数据库 URL 格式"""
        if v is None:
            return None
        if not v:
            raise ValueError("database_url 不能为空")
        # 基本格式检查
        if not (v.startswith("postgresql://") or v.startswith("mysql+pymysql://")):
            raise ValueError(
                "database_url 必须以 postgresql:// 或 mysql+pymysql:// 开头"
            )
        return v
    
    def validate_database_config(self) -> None:
        """
        验证数据库配置是否完整
        
        在应用启动时调用此方法，如果配置缺失会抛出清晰的错误信息。
        
        Raises:
            ValueError: 当 database_url 未配置时抛出
        """
        if not self.database_url:
            raise ValueError(
                "database_url 未配置。请设置环境变量 DATABASE_URL 或在 .env 文件中配置。\n"
                "示例：DATABASE_URL=postgresql://user:password@localhost:5432/dbname"
            )

    # ==================== Redis 配置（可选）====================
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis 连接 URL，格式：redis://host:port/db",
    )

    # ==================== Celery 配置（可选）====================
    celery_broker_url: Optional[str] = Field(
        default=None,
        description="Celery Broker URL，支持 RabbitMQ (amqp://user:password@host:port/vhost) 或 Redis (redis://host:port/db)",
    )
    celery_result_backend: Optional[str] = Field(
        default=None,
        description="Celery 结果后端 URL，支持 Redis (redis://host:port/db) 或 RabbitMQ (rpc://)",
    )
    
    # ==================== Flower 监控配置（可选）====================
    flower_port: int = Field(
        default=5555,
        description="Flower 监控服务端口",
        ge=1,
        le=65535,
    )
    flower_basic_auth: Optional[str] = Field(
        default=None,
        description="Flower 基本认证，格式：username:password（生产环境建议配置）",
    )
    flower_url_prefix: Optional[str] = Field(
        default=None,
        description="Flower URL 前缀（用于反向代理，如 /flower）",
    )

    # ==================== 日志配置 ====================
    log_level: str = Field(
        default="INFO",
        description="日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )
    log_format: str = Field(
        default="json",
        description="日志格式：json 或 text",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"log_level 必须是 {allowed} 之一")
        return v.upper()

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """验证日志格式"""
        allowed = ["json", "text"]
        if v.lower() not in allowed:
            raise ValueError(f"log_format 必须是 {allowed} 之一")
        return v.lower()

    # ==================== CORS 配置 ====================
    # 注意：使用 str 类型存储，避免 Pydantic Settings 尝试 JSON 解析
    # 通过 @computed_field 提供列表形式的访问
    cors_origins_str: Optional[str] = Field(
        default=None,
        alias="CORS_ORIGINS",  # 使用 alias 映射环境变量名
        description="CORS 允许的源列表（字符串格式，多个源用逗号分隔）",
    )

    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        """
        获取 CORS 允许的源列表
        
        如果未配置，返回默认值。
        支持逗号分隔的字符串格式。
        """
        if self.cors_origins_str is None or not self.cors_origins_str.strip():
            return ["http://localhost:3000", "http://localhost:8080"]
        return [
            origin.strip()
            for origin in self.cors_origins_str.split(",")
            if origin.strip()
        ]

    # ==================== 服务器配置 ====================
    host: str = Field(
        default="0.0.0.0",
        description="服务器监听地址",
    )
    port: int = Field(
        default=8000,
        description="服务器监听端口",
        ge=1,
        le=65535,
    )

    # ==================== 配置扩展点 ====================
    # 子类可以继承此类并添加自定义配置项
    # 示例：
    # class CustomSettings(Settings):
    #     custom_config: str = Field(default="default_value")

    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.environment == "development"

    def is_testing(self) -> bool:
        """判断是否为测试环境"""
        return self.environment == "testing"

    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.environment == "production"

    def get_database_url_sync(self, allow_placeholder: bool = False) -> str:
        """
        获取同步数据库 URL
        
        如果使用异步数据库驱动，需要转换 URL。
        
        Args:
            allow_placeholder: 如果为 True，当 database_url 未配置时返回占位符 URL（仅用于生成迁移脚本）
        
        Returns:
            str: 数据库 URL
            
        Raises:
            ValueError: 当 database_url 未配置且 allow_placeholder=False 时抛出
        """
        if not self.database_url:
            if allow_placeholder:
                # 返回占位符 URL（仅用于生成迁移脚本，不会实际连接数据库）
                return "postgresql://user:password@localhost:5432/dbname"
            raise ValueError(
                "database_url 未配置。请先调用 validate_database_config() 验证配置，"
                "或确保设置了 DATABASE_URL 环境变量。"
            )
        return self.database_url

    def get_database_url_async(self) -> str:
        """
        获取异步数据库 URL
        
        将 postgresql:// 转换为 postgresql+asyncpg://
        将 mysql+pymysql:// 转换为 mysql+aiomysql://
        
        Raises:
            ValueError: 当 database_url 未配置时抛出
        """
        if not self.database_url:
            raise ValueError(
                "database_url 未配置。请先调用 validate_database_config() 验证配置，"
                "或确保设置了 DATABASE_URL 环境变量。"
            )
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("mysql+pymysql://"):
            return url.replace("mysql+pymysql://", "mysql+aiomysql://", 1)
        return url


# ==================== IM 项目自定义配置 ====================
class IMSettings(Settings):
    """
    IM 项目自定义配置（继承脚手架配置）
    
    在脚手架配置基础上，扩展 AI 相关配置项。
    """
    
    # ==================== AI 相关配置 ====================
    ai_provider: str = Field(
        default="openai",
        description="AI 服务提供商：openai, anthropic, deepseek",
    )
    
    @field_validator("ai_provider")
    @classmethod
    def validate_ai_provider(cls, v: str) -> str:
        """验证 AI 服务提供商"""
        allowed = ["openai", "anthropic", "deepseek"]
        if v.lower() not in allowed:
            raise ValueError(f"ai_provider 必须是 {allowed} 之一")
        return v.lower()
    
    ai_api_key: Optional[str] = Field(
        default=None,
        description="AI API 密钥",
    )
    
    ai_base_url: Optional[str] = Field(
        default=None,
        description="AI API 基础 URL（可选，某些提供商需要自定义 URL）",
    )
    
    ai_model: str = Field(
        default="gpt-3.5-turbo",
        description="AI 模型名称",
    )
    
    ai_temperature: float = Field(
        default=0.7,
        ge=0,
        le=2,
        description="AI 温度参数（控制回复的随机性）",
    )
    
    ai_max_tokens: int = Field(
        default=1000,
        ge=1,
        description="AI 最大 token 数",
    )


# 创建全局配置实例
# 使用 IM 项目自定义配置
settings = IMSettings()
