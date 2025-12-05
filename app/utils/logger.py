"""
日志工具模块

提供统一的日志记录功能，支持 JSON 和文本两种格式。
根据配置自动选择日志格式和级别。
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.config import settings


class JSONFormatter(logging.Formatter):
    """
    JSON 格式日志格式化器
    
    将日志记录格式化为 JSON 格式，便于日志收集和分析。
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为 JSON 字符串
        
        Args:
            record: 日志记录对象
            
        Returns:
            str: JSON 格式的日志字符串
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加额外字段（如果存在）
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """
    文本格式日志格式化器
    
    提供人类可读的文本格式日志。
    """
    
    def __init__(self):
        """初始化文本格式化器"""
        super().__init__(
            fmt="%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为文本字符串
        
        Args:
            record: 日志记录对象
            
        Returns:
            str: 文本格式的日志字符串
        """
        return super().format(record)


def setup_logger(
    name: Optional[str] = None,
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    设置并返回日志记录器
    
    Args:
        name: 日志记录器名称，默认为根记录器
        log_level: 日志级别，默认从配置读取
        log_format: 日志格式（json/text），默认从配置读取
        log_file: 日志文件路径（可选），如果提供则同时输出到文件
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 获取配置
    level = log_level or settings.log_level
    fmt = log_format or settings.log_format
    
    # 创建日志记录器
    logger = logging.getLogger(name or "app")
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 创建格式化器
    if fmt.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 防止日志传播到根记录器
    logger.propagate = False
    
    return logger


# 创建全局日志记录器
logger = setup_logger("app")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
        
    Example:
        ```python
        from app.utils.logger import get_logger
        
        logger = get_logger(__name__)
        logger.info("这是一条日志")
        ```
    """
    return logging.getLogger(name)


# 导出全局日志记录器
__all__ = ["logger", "get_logger", "setup_logger", "JSONFormatter", "TextFormatter"]

