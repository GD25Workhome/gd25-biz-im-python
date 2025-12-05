"""
自定义异常类模块

提供通用的自定义异常类，便于统一处理错误。
"""

from typing import Any, Optional


class BaseAppException(Exception):
    """
    应用基础异常类
    
    所有自定义异常都应继承此类。
    """
    
    def __init__(
        self,
        message: str = "应用错误",
        code: int = 500,
        details: Optional[Any] = None,
    ):
        """
        初始化异常
        
        Args:
            message: 错误消息
            code: 错误代码
            details: 错误详情
        """
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> dict[str, Any]:
        """
        将异常转换为字典
        
        Returns:
            dict: 包含异常信息的字典
        """
        result = {
            "message": self.message,
            "code": self.code,
        }
        if self.details is not None:
            result["details"] = self.details
        return result


class ValidationError(BaseAppException):
    """
    验证错误异常
    
    用于数据验证失败的情况。
    """
    
    def __init__(self, message: str = "数据验证失败", details: Optional[Any] = None):
        super().__init__(message=message, code=400, details=details)


class NotFoundError(BaseAppException):
    """
    资源未找到异常
    
    用于资源不存在的情况。
    """
    
    def __init__(self, message: str = "资源未找到", details: Optional[Any] = None):
        super().__init__(message=message, code=404, details=details)


class UnauthorizedError(BaseAppException):
    """
    未授权异常
    
    用于认证失败的情况。
    """
    
    def __init__(self, message: str = "未授权", details: Optional[Any] = None):
        super().__init__(message=message, code=401, details=details)


class ForbiddenError(BaseAppException):
    """
    禁止访问异常
    
    用于权限不足的情况。
    """
    
    def __init__(self, message: str = "禁止访问", details: Optional[Any] = None):
        super().__init__(message=message, code=403, details=details)


class ConflictError(BaseAppException):
    """
    冲突异常
    
    用于资源冲突的情况（如重复创建）。
    """
    
    def __init__(self, message: str = "资源冲突", details: Optional[Any] = None):
        super().__init__(message=message, code=409, details=details)


class InternalServerError(BaseAppException):
    """
    内部服务器错误异常
    
    用于服务器内部错误的情况。
    """
    
    def __init__(self, message: str = "内部服务器错误", details: Optional[Any] = None):
        super().__init__(message=message, code=500, details=details)


__all__ = [
    "BaseAppException",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "InternalServerError",
]

