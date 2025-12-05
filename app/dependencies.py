"""
依赖注入模块

提供 FastAPI 依赖注入功能，包括：
- 数据库依赖
- 认证依赖框架（可扩展）
- 权限检查依赖框架（可扩展）

此模块提供了基础框架，项目可以根据实际需求扩展认证和权限检查逻辑。
"""

from typing import Optional, Callable, Protocol, Any
from fastapi import Depends, Request

from app.db.session import get_db as _get_db
from app.utils.exceptions import UnauthorizedError, ForbiddenError


# ==================== 数据库依赖 ====================

# 重新导出数据库依赖，保持统一的依赖注入入口
get_db = _get_db


# ==================== 认证依赖框架 ====================

class AuthenticatedUser(Protocol):
    """
    认证用户协议
    
    定义认证用户对象应具备的基本属性。
    项目可以根据实际需求扩展此协议或创建具体的用户模型。
    """
    id: Any  # 用户ID
    username: Optional[str] = None  # 用户名
    email: Optional[str] = None  # 邮箱


# 全局认证函数（可扩展）
_authentication_function: Optional[Callable[[Request], Optional[AuthenticatedUser]]] = None


def set_authentication_function(
    func: Callable[[Request], Optional[AuthenticatedUser]]
) -> None:
    """
    设置认证函数
    
    项目需要实现自己的认证逻辑时，调用此函数设置认证函数。
    认证函数应该：
    - 接收 FastAPI Request 对象
    - 返回认证用户对象（如果认证成功）
    - 返回 None（如果认证失败，依赖会自动抛出 UnauthorizedError）
    
    Args:
        func: 认证函数，接收 Request，返回用户对象或 None
        
    Example:
        ```python
        from app.dependencies import set_authentication_function, AuthenticatedUser
        from fastapi import Request
        
        def my_auth_function(request: Request) -> Optional[AuthenticatedUser]:
            # 从请求头获取 token
            token = request.headers.get("Authorization")
            if not token:
                return None
            
            # 验证 token 并返回用户对象
            user = verify_token(token)
            return user
        
        # 设置认证函数
        set_authentication_function(my_auth_function)
        ```
    """
    global _authentication_function
    _authentication_function = func


def get_authentication_function() -> Optional[Callable[[Request], Optional[AuthenticatedUser]]]:
    """
    获取当前设置的认证函数
    
    Returns:
        认证函数或 None
    """
    return _authentication_function


def get_current_user(
    request: Request,
    auth_func: Optional[Callable[[Request], Optional[AuthenticatedUser]]] = None
) -> AuthenticatedUser:
    """
    获取当前认证用户依赖
    
    此依赖用于需要认证的路由中，会自动验证用户身份。
    如果认证失败，会抛出 UnauthorizedError（401）。
    
    Args:
        request: FastAPI Request 对象（自动注入）
        auth_func: 可选的认证函数，如果不提供则使用全局设置的认证函数
        
    Returns:
        AuthenticatedUser: 认证用户对象
        
    Raises:
        UnauthorizedError: 当认证失败时抛出
        
    Example:
        ```python
        from fastapi import Depends
        from app.dependencies import get_current_user
        
        @app.get("/profile")
        def get_profile(user = Depends(get_current_user)):
            return {"user_id": user.id, "username": user.username}
        ```
    """
    # 使用传入的认证函数或全局认证函数
    auth_function = auth_func or _authentication_function
    
    if auth_function is None:
        raise UnauthorizedError(
            message="认证功能未配置，请先设置认证函数",
            details="调用 set_authentication_function() 设置认证函数"
        )
    
    # 执行认证
    user = auth_function(request)
    
    if user is None:
        raise UnauthorizedError(message="认证失败，请提供有效的认证信息")
    
    return user


# ==================== 权限检查依赖框架 ====================

class PermissionChecker(Protocol):
    """
    权限检查器协议
    
    定义权限检查器应具备的方法。
    项目可以根据实际需求实现具体的权限检查逻辑。
    """
    def check(self, user: AuthenticatedUser, resource: Optional[str] = None, action: Optional[str] = None) -> bool:
        """
        检查用户是否有权限
        
        Args:
            user: 认证用户对象
            resource: 资源标识（可选）
            action: 操作类型（可选）
            
        Returns:
            bool: 有权限返回 True，否则返回 False
        """
        ...


# 全局权限检查函数（可扩展）
_permission_check_function: Optional[Callable[[AuthenticatedUser, Optional[str], Optional[str]], bool]] = None


def set_permission_check_function(
    func: Callable[[AuthenticatedUser, Optional[str], Optional[str]], bool]
) -> None:
    """
    设置权限检查函数
    
    项目需要实现自己的权限检查逻辑时，调用此函数设置权限检查函数。
    权限检查函数应该：
    - 接收认证用户对象、资源标识（可选）、操作类型（可选）
    - 返回 True（有权限）或 False（无权限）
    
    Args:
        func: 权限检查函数
        
    Example:
        ```python
        from app.dependencies import set_permission_check_function, AuthenticatedUser
        
        def my_permission_check(
            user: AuthenticatedUser,
            resource: Optional[str] = None,
            action: Optional[str] = None
        ) -> bool:
            # 实现权限检查逻辑
            if resource == "admin" and user.role != "admin":
                return False
            return True
        
        # 设置权限检查函数
        set_permission_check_function(my_permission_check)
        ```
    """
    global _permission_check_function
    _permission_check_function = func


def get_permission_check_function() -> Optional[Callable[[AuthenticatedUser, Optional[str], Optional[str]], bool]]:
    """
    获取当前设置的权限检查函数
    
    Returns:
        权限检查函数或 None
    """
    return _permission_check_function


def require_permission(
    resource: Optional[str] = None,
    action: Optional[str] = None,
    user: AuthenticatedUser = Depends(get_current_user),
    check_func: Optional[Callable[[AuthenticatedUser, Optional[str], Optional[str]], bool]] = None
) -> AuthenticatedUser:
    """
    权限检查依赖
    
    此依赖用于需要特定权限的路由中，会自动检查用户权限。
    如果权限检查失败，会抛出 ForbiddenError（403）。
    
    Args:
        resource: 资源标识（可选）
        action: 操作类型（可选）
        user: 认证用户对象（自动注入）
        check_func: 可选的权限检查函数，如果不提供则使用全局设置的权限检查函数
        
    Returns:
        AuthenticatedUser: 认证用户对象（权限检查通过后）
        
    Raises:
        ForbiddenError: 当权限检查失败时抛出
        
    Example:
        ```python
        from fastapi import Depends
        from app.dependencies import require_permission
        
        @app.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            user = Depends(require_permission(resource="user", action="delete"))
        ):
            # 只有有权限的用户才能执行删除操作
            return {"message": "用户已删除"}
        ```
    """
    # 使用传入的权限检查函数或全局权限检查函数
    permission_check = check_func or _permission_check_function
    
    if permission_check is None:
        raise ForbiddenError(
            message="权限检查功能未配置，请先设置权限检查函数",
            details="调用 set_permission_check_function() 设置权限检查函数"
        )
    
    # 执行权限检查
    has_permission = permission_check(user, resource, action)
    
    if not has_permission:
        error_msg = "权限不足"
        if resource or action:
            details = []
            if resource:
                details.append(f"资源: {resource}")
            if action:
                details.append(f"操作: {action}")
            error_msg += f"（{', '.join(details)}）"
        raise ForbiddenError(message=error_msg)
    
    return user


# ==================== 便捷函数 ====================

def create_permission_dependency(
    resource: Optional[str] = None,
    action: Optional[str] = None
) -> Callable:
    """
    创建权限检查依赖的便捷函数
    
    用于创建特定资源/操作的权限检查依赖。
    
    Args:
        resource: 资源标识
        action: 操作类型
        
    Returns:
        权限检查依赖函数
        
    Example:
        ```python
        from app.dependencies import create_permission_dependency
        
        # 创建删除用户的权限检查依赖
        require_delete_user = create_permission_dependency(resource="user", action="delete")
        
        @app.delete("/users/{user_id}")
        def delete_user(user_id: int, user = Depends(require_delete_user)):
            return {"message": "用户已删除"}
        ```
    """
    def permission_dependency(
        user: AuthenticatedUser = Depends(get_current_user)
    ) -> AuthenticatedUser:
        return require_permission(resource=resource, action=action, user=user)
    
    return permission_dependency


# ==================== 导出 ====================

__all__ = [
    # 数据库依赖
    "get_db",
    # 认证相关
    "AuthenticatedUser",
    "set_authentication_function",
    "get_authentication_function",
    "get_current_user",
    # 权限检查相关
    "PermissionChecker",
    "set_permission_check_function",
    "get_permission_check_function",
    "require_permission",
    "create_permission_dependency",
]

