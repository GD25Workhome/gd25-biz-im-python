"""
ID 生成器模块

提供通用的唯一 ID 生成功能，支持自定义前缀和时间戳+UUID 组合。
"""

import uuid
from datetime import datetime
from typing import Optional


def generate_id(prefix: Optional[str] = None, include_timestamp: bool = True) -> str:
    """
    生成唯一 ID
    
    生成格式：{prefix}_{timestamp}_{uuid} 或 {prefix}_{uuid}
    如果 prefix 为 None，则不包含前缀。
    
    Args:
        prefix: ID 前缀（可选），例如 "msg", "user", "order" 等
        include_timestamp: 是否包含时间戳，默认为 True
        
    Returns:
        str: 生成的唯一 ID
        
    Example:
        ```python
        from app.utils.id_generator import generate_id
        
        # 生成带前缀和时间戳的 ID
        msg_id = generate_id("msg")
        # 输出: msg_20250127123456_a1b2c3d4-e5f6-7890-abcd-ef1234567890
        
        # 生成不带时间戳的 ID
        user_id = generate_id("user", include_timestamp=False)
        # 输出: user_a1b2c3d4-e5f6-7890-abcd-ef1234567890
        
        # 生成不带前缀的 ID
        id = generate_id()
        # 输出: 20250127123456_a1b2c3d4-e5f6-7890-abcd-ef1234567890
        ```
    """
    # 生成 UUID（去掉连字符，使用短格式）
    uuid_str = str(uuid.uuid4()).replace("-", "")
    
    parts = []
    
    # 添加前缀
    if prefix:
        parts.append(prefix)
    
    # 添加时间戳（格式：YYYYMMDDHHMMSS）
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        parts.append(timestamp)
    
    # 添加 UUID
    parts.append(uuid_str)
    
    # 用下划线连接所有部分
    return "_".join(parts)


def generate_short_id(prefix: Optional[str] = None, length: int = 8) -> str:
    """
    生成短 ID（使用 UUID 的前 N 位）
    
    适用于需要较短 ID 的场景，但唯一性相对较低。
    
    Args:
        prefix: ID 前缀（可选）
        length: UUID 部分长度，默认为 8
        
    Returns:
        str: 生成的短 ID
        
    Example:
        ```python
        from app.utils.id_generator import generate_short_id
        
        short_id = generate_short_id("order", length=8)
        # 输出: order_a1b2c3d4
        ```
    """
    # 生成 UUID 并取前 length 位
    uuid_str = str(uuid.uuid4()).replace("-", "")[:length]
    
    if prefix:
        return f"{prefix}_{uuid_str}"
    return uuid_str


def generate_numeric_id(prefix: Optional[str] = None) -> str:
    """
    生成数字 ID（基于时间戳和随机数）
    
    生成格式：{prefix}_{timestamp}{random}
    
    Args:
        prefix: ID 前缀（可选）
        
    Returns:
        str: 生成的数字 ID
        
    Example:
        ```python
        from app.utils.id_generator import generate_numeric_id
        
        numeric_id = generate_numeric_id("order")
        # 输出: order_20250127123456123456
        ```
    """
    # 时间戳（微秒精度）
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    # 添加随机数（使用 UUID 的数字部分）
    import random
    random_part = str(random.randint(1000, 9999))
    
    numeric_str = f"{timestamp}{random_part}"
    
    if prefix:
        return f"{prefix}_{numeric_str}"
    return numeric_str


__all__ = ["generate_id", "generate_short_id", "generate_numeric_id"]

