# 测试工具类模块
import sys
import json
import logging
import tempfile
from pathlib import Path
from io import StringIO

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试日志工具
from app.utils.logger import (
    logger,
    get_logger,
    setup_logger,
    JSONFormatter,
    TextFormatter,
)

# 测试 ID 生成器
from app.utils.id_generator import (
    generate_id,
    generate_short_id,
    generate_numeric_id,
)

# 测试统一响应格式
from app.utils.response import (
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    success_response,
    error_response,
)

# 测试自定义异常类
from app.utils.exceptions import (
    BaseAppException,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    InternalServerError,
)


# ==================== 日志工具测试 ====================

def test_logger_basic():
    """测试基本日志输出"""
    print("\n=== 测试基本日志输出 ===")
    
    # 测试 info 日志
    logger.info("测试日志输出")
    
    # 测试 error 日志
    logger.error("测试错误日志")
    
    print("✓ 基本日志输出测试通过")


def test_logger_json_format():
    """测试 JSON 格式日志"""
    print("\n=== 测试 JSON 格式日志 ===")
    
    # 创建临时字符串流来捕获日志输出
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(JSONFormatter())
    
    test_logger = logging.getLogger("test_json")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(handler)
    test_logger.propagate = False
    
    # 记录日志
    test_logger.info("测试 JSON 格式")
    
    # 验证输出是有效的 JSON
    output = log_stream.getvalue()
    assert output.strip() != "", "日志输出不应为空"
    
    # 解析 JSON
    log_data = json.loads(output.strip())
    assert "timestamp" in log_data
    assert "level" in log_data
    assert "message" in log_data
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "测试 JSON 格式"
    
    print("✓ JSON 格式日志测试通过")


def test_logger_text_format():
    """测试文本格式日志"""
    print("\n=== 测试文本格式日志 ===")
    
    # 创建临时字符串流来捕获日志输出
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(TextFormatter())
    
    test_logger = logging.getLogger("test_text")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(handler)
    test_logger.propagate = False
    
    # 记录日志
    test_logger.info("测试文本格式")
    
    # 验证输出包含关键信息
    output = log_stream.getvalue()
    assert "测试文本格式" in output
    assert "INFO" in output
    
    print("✓ 文本格式日志测试通过")


def test_logger_file_output():
    """测试日志文件输出"""
    print("\n=== 测试日志文件输出 ===")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        log_file = f.name
    
    try:
        # 创建文件日志记录器
        file_logger = setup_logger("test_file", log_format="text", log_file=log_file)
        file_logger.info("测试文件日志")
        
        # 验证文件内容
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "测试文件日志" in content
        
        print("✓ 日志文件输出测试通过")
    finally:
        # 清理临时文件
        Path(log_file).unlink(missing_ok=True)


def test_get_logger():
    """测试获取指定名称的日志记录器"""
    print("\n=== 测试获取日志记录器 ===")
    
    custom_logger = get_logger("custom_module")
    assert custom_logger is not None
    assert custom_logger.name == "custom_module"
    
    print("✓ 获取日志记录器测试通过")


# ==================== ID 生成器测试 ====================

def test_generate_id_basic():
    """测试基本 ID 生成（开发计划中的测试用例）"""
    print("\n=== 测试基本 ID 生成 ===")
    
    id1 = generate_id("msg")
    id2 = generate_id("msg")
    
    # 验证唯一性
    assert id1 != id2, "生成的 ID 应该是唯一的"
    
    # 验证前缀
    assert id1.startswith("msg_"), f"ID 应该以 'msg_' 开头，实际: {id1}"
    
    print(f"✓ 生成的 ID1: {id1}")
    print(f"✓ 生成的 ID2: {id2}")
    print("✓ 基本 ID 生成测试通过")


def test_generate_id_with_prefix():
    """测试带前缀的 ID 生成"""
    print("\n=== 测试带前缀的 ID 生成 ===")
    
    # 测试不同前缀
    user_id = generate_id("user")
    order_id = generate_id("order")
    
    assert user_id.startswith("user_")
    assert order_id.startswith("order_")
    
    print(f"✓ 用户 ID: {user_id}")
    print(f"✓ 订单 ID: {order_id}")
    print("✓ 带前缀的 ID 生成测试通过")


def test_generate_id_without_prefix():
    """测试不带前缀的 ID 生成"""
    print("\n=== 测试不带前缀的 ID 生成 ===")
    
    id_without_prefix = generate_id()
    
    # 应该以时间戳开头（格式：YYYYMMDDHHMMSS）
    assert len(id_without_prefix) > 14, "ID 应该包含时间戳和 UUID"
    
    print(f"✓ 无前缀 ID: {id_without_prefix}")
    print("✓ 不带前缀的 ID 生成测试通过")


def test_generate_id_without_timestamp():
    """测试不带时间戳的 ID 生成"""
    print("\n=== 测试不带时间戳的 ID 生成 ===")
    
    id_no_timestamp = generate_id("test", include_timestamp=False)
    
    # 应该只包含前缀和 UUID
    assert id_no_timestamp.startswith("test_")
    parts = id_no_timestamp.split("_")
    assert len(parts) == 2, "应该只有前缀和 UUID 两部分"
    
    print(f"✓ 无时间戳 ID: {id_no_timestamp}")
    print("✓ 不带时间戳的 ID 生成测试通过")


def test_generate_id_uniqueness():
    """测试 ID 唯一性"""
    print("\n=== 测试 ID 唯一性 ===")
    
    # 生成多个 ID
    ids = [generate_id("test") for _ in range(100)]
    
    # 验证所有 ID 都是唯一的
    assert len(ids) == len(set(ids)), "所有生成的 ID 应该是唯一的"
    
    print(f"✓ 生成了 {len(ids)} 个唯一 ID")
    print("✓ ID 唯一性测试通过")


def test_generate_short_id():
    """测试短 ID 生成"""
    print("\n=== 测试短 ID 生成 ===")
    
    short_id = generate_short_id("order", length=8)
    
    assert short_id.startswith("order_")
    parts = short_id.split("_")
    assert len(parts[1]) == 8, "UUID 部分应该是 8 位"
    
    print(f"✓ 短 ID: {short_id}")
    print("✓ 短 ID 生成测试通过")


def test_generate_numeric_id():
    """测试数字 ID 生成"""
    print("\n=== 测试数字 ID 生成 ===")
    
    numeric_id = generate_numeric_id("order")
    
    assert numeric_id.startswith("order_")
    # 验证数字部分只包含数字
    numeric_part = numeric_id.split("_")[1]
    assert numeric_part.isdigit(), "数字 ID 应该只包含数字"
    
    print(f"✓ 数字 ID: {numeric_id}")
    print("✓ 数字 ID 生成测试通过")


# ==================== 统一响应格式测试 ====================

def test_success_response():
    """测试成功响应"""
    print("\n=== 测试成功响应 ===")
    
    response = success_response(data={"user_id": 123}, message="用户创建成功")
    
    assert response["code"] == 200
    assert response["message"] == "用户创建成功"
    assert response["data"]["user_id"] == 123
    assert "timestamp" in response
    
    print(f"✓ 成功响应: {response}")
    print("✓ 成功响应测试通过")


def test_error_response():
    """测试错误响应"""
    print("\n=== 测试错误响应 ===")
    
    response = error_response(message="用户不存在", code=404)
    
    assert response["code"] == 404
    assert response["message"] == "用户不存在"
    assert "timestamp" in response
    
    print(f"✓ 错误响应: {response}")
    print("✓ 错误响应测试通过")


def test_base_response_model():
    """测试基础响应模型"""
    print("\n=== 测试基础响应模型 ===")
    
    # 测试 SuccessResponse
    success = SuccessResponse(data={"result": "ok"})
    assert success.code == 200
    assert success.message == "success"
    assert success.data["result"] == "ok"
    assert success.timestamp is not None
    
    # 测试 ErrorResponse
    error = ErrorResponse(message="测试错误", code=400)
    assert error.code == 400
    assert error.message == "测试错误"
    assert error.data is None
    
    print("✓ 基础响应模型测试通过")


# ==================== 自定义异常类测试 ====================

def test_base_app_exception():
    """测试基础异常类"""
    print("\n=== 测试基础异常类 ===")
    
    exception = BaseAppException(message="测试错误", code=500, details={"key": "value"})
    
    assert exception.message == "测试错误"
    assert exception.code == 500
    assert exception.details == {"key": "value"}
    
    # 测试转换为字典
    exception_dict = exception.to_dict()
    assert exception_dict["message"] == "测试错误"
    assert exception_dict["code"] == 500
    assert exception_dict["details"] == {"key": "value"}
    
    print("✓ 基础异常类测试通过")


def test_validation_error():
    """测试验证错误异常"""
    print("\n=== 测试验证错误异常 ===")
    
    error = ValidationError(message="数据格式错误", details={"field": "email"})
    
    assert error.message == "数据格式错误"
    assert error.code == 400
    assert error.details == {"field": "email"}
    
    print("✓ 验证错误异常测试通过")


def test_not_found_error():
    """测试未找到异常"""
    print("\n=== 测试未找到异常 ===")
    
    error = NotFoundError(message="用户不存在")
    
    assert error.message == "用户不存在"
    assert error.code == 404
    
    print("✓ 未找到异常测试通过")


def test_unauthorized_error():
    """测试未授权异常"""
    print("\n=== 测试未授权异常 ===")
    
    error = UnauthorizedError()
    
    assert error.message == "未授权"
    assert error.code == 401
    
    print("✓ 未授权异常测试通过")


def test_forbidden_error():
    """测试禁止访问异常"""
    print("\n=== 测试禁止访问异常 ===")
    
    error = ForbiddenError()
    
    assert error.message == "禁止访问"
    assert error.code == 403
    
    print("✓ 禁止访问异常测试通过")


def test_conflict_error():
    """测试冲突异常"""
    print("\n=== 测试冲突异常 ===")
    
    error = ConflictError(message="资源已存在")
    
    assert error.message == "资源已存在"
    assert error.code == 409
    
    print("✓ 冲突异常测试通过")


def test_internal_server_error():
    """测试内部服务器错误异常"""
    print("\n=== 测试内部服务器错误异常 ===")
    
    error = InternalServerError()
    
    assert error.message == "内部服务器错误"
    assert error.code == 500
    
    print("✓ 内部服务器错误异常测试通过")


# ==================== 主测试函数 ====================

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试工具类模块")
    print("=" * 60)
    
    try:
        # 日志工具测试
        test_logger_basic()
        test_logger_json_format()
        test_logger_text_format()
        test_logger_file_output()
        test_get_logger()
        
        # ID 生成器测试
        test_generate_id_basic()
        test_generate_id_with_prefix()
        test_generate_id_without_prefix()
        test_generate_id_without_timestamp()
        test_generate_id_uniqueness()
        test_generate_short_id()
        test_generate_numeric_id()
        
        # 统一响应格式测试
        test_success_response()
        test_error_response()
        test_base_response_model()
        
        # 自定义异常类测试
        test_base_app_exception()
        test_validation_error()
        test_not_found_error()
        test_unauthorized_error()
        test_forbidden_error()
        test_conflict_error()
        test_internal_server_error()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_tests()

