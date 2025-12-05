# 测试依赖注入模块
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Optional

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.dependencies import (
    get_db,
    AuthenticatedUser,
    set_authentication_function,
    get_authentication_function,
    get_current_user,
    set_permission_check_function,
    get_permission_check_function,
    require_permission,
    create_permission_dependency,
)
from app.utils.exceptions import UnauthorizedError, ForbiddenError
from sqlalchemy.orm import Session


# ==================== 测试辅助类 ====================

class MockUser:
    """模拟用户对象，用于测试"""
    def __init__(self, user_id: str, username: Optional[str] = None, email: Optional[str] = None, role: Optional[str] = None):
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role


# ==================== 数据库依赖测试 ====================

def test_get_db():
    """测试数据库依赖"""
    print("\n=== 测试数据库依赖 ===")
    
    # 测试 get_db 是一个生成器函数
    db_gen = get_db()
    assert db_gen is not None, "get_db 应该返回生成器"
    
    # 获取数据库会话
    db = next(db_gen)
    assert db is not None, "数据库会话不应为 None"
    assert isinstance(db, Session), "应该返回 Session 对象"
    
    # 测试会话可以正常使用
    try:
        # 测试查询（如果数据库可用）
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        assert result is not None
    except Exception:
        # 如果数据库不可用，至少验证会话对象存在
        pass
    
    # 关闭生成器
    try:
        next(db_gen)
    except StopIteration:
        pass
    
    print("✓ 数据库依赖测试通过")


# ==================== 认证依赖框架测试 ====================

def test_set_and_get_authentication_function():
    """测试设置和获取认证函数"""
    print("\n=== 测试设置和获取认证函数 ===")
    
    # 保存原始函数
    original_func = get_authentication_function()
    
    # 创建模拟认证函数
    def mock_auth_func(request):
        return MockUser("user_123", "testuser")
    
    # 设置认证函数
    set_authentication_function(mock_auth_func)
    
    # 验证设置成功
    retrieved_func = get_authentication_function()
    assert retrieved_func is not None, "应该能够获取认证函数"
    assert retrieved_func == mock_auth_func, "获取的函数应该与设置的函数相同"
    
    # 恢复原始函数
    if original_func is not None:
        set_authentication_function(original_func)
    else:
        # 清除设置的函数（通过设置 None 的方式）
        set_authentication_function(lambda r: None)
        set_authentication_function(None)
    
    print("✓ 设置和获取认证函数测试通过")


def test_get_current_user_success():
    """测试获取当前用户（成功情况）"""
    print("\n=== 测试获取当前用户（成功） ===")
    
    # 创建模拟用户
    mock_user = MockUser("user_123", "testuser", "test@example.com")
    
    # 创建模拟认证函数
    def mock_auth_func(request):
        return mock_user
    
    # 设置认证函数
    set_authentication_function(mock_auth_func)
    
    # 创建模拟 Request 对象
    mock_request = Mock()
    
    # 测试获取当前用户
    user = get_current_user(mock_request)
    assert user is not None, "应该返回用户对象"
    assert user.id == "user_123", "用户 ID 应该正确"
    assert user.username == "testuser", "用户名应该正确"
    
    # 清理
    set_authentication_function(None)
    
    print("✓ 获取当前用户（成功）测试通过")


def test_get_current_user_no_auth_function():
    """测试获取当前用户（未设置认证函数）"""
    print("\n=== 测试获取当前用户（未设置认证函数） ===")
    
    # 清除认证函数
    set_authentication_function(None)
    
    # 创建模拟 Request 对象
    mock_request = Mock()
    
    # 测试应该抛出异常
    try:
        get_current_user(mock_request)
        assert False, "应该抛出 UnauthorizedError"
    except UnauthorizedError as e:
        assert e.code == 401, "错误代码应该是 401"
        assert "认证功能未配置" in e.message, "错误消息应该包含提示信息"
        print("✓ 正确抛出 UnauthorizedError")
    
    print("✓ 获取当前用户（未设置认证函数）测试通过")


def test_get_current_user_auth_failed():
    """测试获取当前用户（认证失败）"""
    print("\n=== 测试获取当前用户（认证失败） ===")
    
    # 创建返回 None 的认证函数（模拟认证失败）
    def mock_auth_func(request):
        return None
    
    # 设置认证函数
    set_authentication_function(mock_auth_func)
    
    # 创建模拟 Request 对象
    mock_request = Mock()
    
    # 测试应该抛出异常
    try:
        get_current_user(mock_request)
        assert False, "应该抛出 UnauthorizedError"
    except UnauthorizedError as e:
        assert e.code == 401, "错误代码应该是 401"
        assert "认证失败" in e.message, "错误消息应该包含认证失败信息"
        print("✓ 正确抛出 UnauthorizedError")
    
    # 清理
    set_authentication_function(None)
    
    print("✓ 获取当前用户（认证失败）测试通过")


def test_get_current_user_with_custom_auth_func():
    """测试使用自定义认证函数"""
    print("\n=== 测试使用自定义认证函数 ===")
    
    # 创建模拟用户
    mock_user = MockUser("user_456", "customuser")
    
    # 创建自定义认证函数
    def custom_auth_func(request):
        return mock_user
    
    # 创建模拟 Request 对象
    mock_request = Mock()
    
    # 测试使用自定义认证函数
    user = get_current_user(mock_request, auth_func=custom_auth_func)
    assert user is not None, "应该返回用户对象"
    assert user.id == "user_456", "用户 ID 应该正确"
    assert user.username == "customuser", "用户名应该正确"
    
    print("✓ 使用自定义认证函数测试通过")


# ==================== 权限检查依赖框架测试 ====================

def test_set_and_get_permission_check_function():
    """测试设置和获取权限检查函数"""
    print("\n=== 测试设置和获取权限检查函数 ===")
    
    # 保存原始函数
    original_func = get_permission_check_function()
    
    # 创建模拟权限检查函数
    def mock_permission_check(user, resource=None, action=None):
        return True
    
    # 设置权限检查函数
    set_permission_check_function(mock_permission_check)
    
    # 验证设置成功
    retrieved_func = get_permission_check_function()
    assert retrieved_func is not None, "应该能够获取权限检查函数"
    assert retrieved_func == mock_permission_check, "获取的函数应该与设置的函数相同"
    
    # 恢复原始函数
    if original_func is not None:
        set_permission_check_function(original_func)
    else:
        set_permission_check_function(None)
    
    print("✓ 设置和获取权限检查函数测试通过")


def test_require_permission_success():
    """测试权限检查（成功情况）"""
    print("\n=== 测试权限检查（成功） ===")
    
    # 创建模拟用户
    mock_user = MockUser("user_123", "testuser")
    
    # 创建模拟权限检查函数（总是返回 True）
    def mock_permission_check(user, resource=None, action=None):
        return True
    
    # 设置权限检查函数
    set_permission_check_function(mock_permission_check)
    
    # 设置认证函数
    def mock_auth_func(request):
        return mock_user
    
    set_authentication_function(mock_auth_func)
    
    # 创建模拟 Request 对象
    mock_request = Mock()
    
    # 先获取用户
    user = get_current_user(mock_request)
    
    # 测试权限检查
    result_user = require_permission(resource="user", action="delete", user=user)
    assert result_user is not None, "应该返回用户对象"
    assert result_user.id == "user_123", "用户 ID 应该正确"
    
    # 清理
    set_permission_check_function(None)
    set_authentication_function(None)
    
    print("✓ 权限检查（成功）测试通过")


def test_require_permission_failed():
    """测试权限检查（失败情况）"""
    print("\n=== 测试权限检查（失败） ===")
    
    # 创建模拟用户
    mock_user = MockUser("user_123", "testuser")
    
    # 创建模拟权限检查函数（总是返回 False）
    def mock_permission_check(user, resource=None, action=None):
        return False
    
    # 设置权限检查函数
    set_permission_check_function(mock_permission_check)
    
    # 测试应该抛出异常
    try:
        require_permission(resource="user", action="delete", user=mock_user)
        assert False, "应该抛出 ForbiddenError"
    except ForbiddenError as e:
        assert e.code == 403, "错误代码应该是 403"
        assert "权限不足" in e.message, "错误消息应该包含权限不足信息"
        assert "资源: user" in e.message, "错误消息应该包含资源信息"
        assert "操作: delete" in e.message, "错误消息应该包含操作信息"
        print("✓ 正确抛出 ForbiddenError")
    
    # 清理
    set_permission_check_function(None)
    
    print("✓ 权限检查（失败）测试通过")


def test_require_permission_no_check_function():
    """测试权限检查（未设置权限检查函数）"""
    print("\n=== 测试权限检查（未设置权限检查函数） ===")
    
    # 清除权限检查函数
    set_permission_check_function(None)
    
    # 创建模拟用户
    mock_user = MockUser("user_123", "testuser")
    
    # 测试应该抛出异常
    try:
        require_permission(resource="user", action="delete", user=mock_user)
        assert False, "应该抛出 ForbiddenError"
    except ForbiddenError as e:
        assert e.code == 403, "错误代码应该是 403"
        assert "权限检查功能未配置" in e.message, "错误消息应该包含提示信息"
        print("✓ 正确抛出 ForbiddenError")
    
    print("✓ 权限检查（未设置权限检查函数）测试通过")


def test_require_permission_with_custom_check_func():
    """测试使用自定义权限检查函数"""
    print("\n=== 测试使用自定义权限检查函数 ===")
    
    # 创建模拟用户
    mock_user = MockUser("user_123", "testuser", role="admin")
    
    # 创建自定义权限检查函数（检查用户角色）
    def custom_permission_check(user, resource=None, action=None):
        if hasattr(user, 'role') and user.role == "admin":
            return True
        return False
    
    # 测试使用自定义权限检查函数
    result_user = require_permission(
        resource="admin",
        action="manage",
        user=mock_user,
        check_func=custom_permission_check
    )
    assert result_user is not None, "应该返回用户对象"
    assert result_user.id == "user_123", "用户 ID 应该正确"
    
    # 测试权限不足的情况
    mock_user_no_admin = MockUser("user_456", "normaluser", role="user")
    try:
        require_permission(
            resource="admin",
            action="manage",
            user=mock_user_no_admin,
            check_func=custom_permission_check
        )
        assert False, "应该抛出 ForbiddenError"
    except ForbiddenError as e:
        assert e.code == 403, "错误代码应该是 403"
        print("✓ 正确抛出 ForbiddenError（权限不足）")
    
    print("✓ 使用自定义权限检查函数测试通过")


def test_require_permission_with_resource_and_action():
    """测试权限检查（带资源和操作参数）"""
    print("\n=== 测试权限检查（带资源和操作参数） ===")
    
    # 创建模拟用户
    mock_user = MockUser("user_123", "testuser")
    
    # 创建模拟权限检查函数（检查资源和操作）
    def mock_permission_check(user, resource=None, action=None):
        if resource == "user" and action == "delete":
            return True
        return False
    
    # 设置权限检查函数
    set_permission_check_function(mock_permission_check)
    
    # 测试有权限的情况
    result_user = require_permission(resource="user", action="delete", user=mock_user)
    assert result_user is not None, "应该返回用户对象"
    
    # 测试无权限的情况
    try:
        require_permission(resource="admin", action="manage", user=mock_user)
        assert False, "应该抛出 ForbiddenError"
    except ForbiddenError as e:
        assert e.code == 403, "错误代码应该是 403"
        print("✓ 正确抛出 ForbiddenError（无权限）")
    
    # 清理
    set_permission_check_function(None)
    
    print("✓ 权限检查（带资源和操作参数）测试通过")


# ==================== 便捷函数测试 ====================

def test_create_permission_dependency():
    """测试创建权限检查依赖的便捷函数"""
    print("\n=== 测试创建权限检查依赖的便捷函数 ===")
    
    # 创建模拟用户
    mock_user = MockUser("user_123", "testuser")
    
    # 创建模拟权限检查函数
    def mock_permission_check(user, resource=None, action=None):
        if resource == "user" and action == "delete":
            return True
        return False
    
    # 设置权限检查函数
    set_permission_check_function(mock_permission_check)
    
    # 创建权限检查依赖
    require_delete_user = create_permission_dependency(resource="user", action="delete")
    assert callable(require_delete_user), "应该返回可调用对象"
    
    # 测试依赖函数
    result_user = require_delete_user(user=mock_user)
    assert result_user is not None, "应该返回用户对象"
    assert result_user.id == "user_123", "用户 ID 应该正确"
    
    # 清理
    set_permission_check_function(None)
    
    print("✓ 创建权限检查依赖的便捷函数测试通过")


# ==================== 集成测试 ====================

def test_authentication_and_permission_integration():
    """测试认证和权限检查的集成"""
    print("\n=== 测试认证和权限检查的集成 ===")
    
    # 创建模拟用户
    admin_user = MockUser("admin_123", "admin", role="admin")
    normal_user = MockUser("user_123", "normal", role="user")
    
    # 设置认证函数
    def mock_auth_func(request):
        # 根据请求头返回不同的用户
        auth_header = getattr(request, 'headers', {}).get('Authorization', '')
        if 'admin' in auth_header:
            return admin_user
        elif 'user' in auth_header:
            return normal_user
        return None
    
    set_authentication_function(mock_auth_func)
    
    # 设置权限检查函数
    def mock_permission_check(user, resource=None, action=None):
        if hasattr(user, 'role'):
            if user.role == "admin":
                return True
            elif user.role == "user" and resource == "user" and action == "read":
                return True
        return False
    
    set_permission_check_function(mock_permission_check)
    
    # 创建模拟 Request 对象（管理员）
    admin_request = Mock()
    admin_request.headers = {"Authorization": "admin_token"}
    
    # 测试管理员可以访问所有资源
    admin = get_current_user(admin_request)
    result = require_permission(resource="admin", action="manage", user=admin)
    assert result is not None, "管理员应该有权限"
    
    # 创建模拟 Request 对象（普通用户）
    user_request = Mock()
    user_request.headers = {"Authorization": "user_token"}
    
    # 测试普通用户可以读取用户资源
    user = get_current_user(user_request)
    result = require_permission(resource="user", action="read", user=user)
    assert result is not None, "普通用户应该有读取权限"
    
    # 测试普通用户不能管理管理员资源
    try:
        require_permission(resource="admin", action="manage", user=user)
        assert False, "应该抛出 ForbiddenError"
    except ForbiddenError as e:
        assert e.code == 403, "错误代码应该是 403"
        print("✓ 正确抛出 ForbiddenError（普通用户无管理权限）")
    
    # 清理
    set_authentication_function(None)
    set_permission_check_function(None)
    
    print("✓ 认证和权限检查的集成测试通过")


# ==================== 运行所有测试 ====================

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试依赖注入模块")
    print("=" * 60)
    
    try:
        # 数据库依赖测试
        test_get_db()
        
        # 认证依赖框架测试
        test_set_and_get_authentication_function()
        test_get_current_user_success()
        test_get_current_user_no_auth_function()
        test_get_current_user_auth_failed()
        test_get_current_user_with_custom_auth_func()
        
        # 权限检查依赖框架测试
        test_set_and_get_permission_check_function()
        test_require_permission_success()
        test_require_permission_failed()
        test_require_permission_no_check_function()
        test_require_permission_with_custom_check_func()
        test_require_permission_with_resource_and_action()
        
        # 便捷函数测试
        test_create_permission_dependency()
        
        # 集成测试
        test_authentication_and_permission_integration()
        
        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_tests()

