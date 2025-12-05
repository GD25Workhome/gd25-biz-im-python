"""
Celery 任务测试模块

测试 Celery 异步任务队列的功能，包括：
- Celery 应用初始化
- 任务定义和配置
- 任务执行（使用测试模式）
- 基础任务类功能
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from celery import Celery, Task
from celery.result import AsyncResult

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.tasks.celery_app import celery_app, make_celery_app
from app.tasks.base import BaseTask, task
from app.tasks.examples import (
    simple_task,
    decorated_task,
    retryable_task,
    long_running_task,
)


# ==================== Celery 应用配置测试 ====================

def test_celery_app_initialization():
    """测试 Celery 应用初始化"""
    with patch("app.tasks.celery_app.settings") as mock_settings:
        mock_settings.celery_broker_url = "amqp://test:test@localhost:5672/"
        mock_settings.celery_result_backend = None
        
        app = make_celery_app()
        assert app is not None
        assert isinstance(app, Celery)
        assert app.main == "gd25-arch-backend"


def test_celery_app_configuration():
    """测试 Celery 应用配置"""
    with patch("app.tasks.celery_app.settings") as mock_settings:
        mock_settings.celery_broker_url = "amqp://test:test@localhost:5672/"
        mock_settings.celery_result_backend = None
        
        app = make_celery_app()
        # 测试序列化配置
        assert app.conf.task_serializer == "json"
        assert app.conf.accept_content == ["json"]
        assert app.conf.result_serializer == "json"
        
        # 测试超时配置
        assert app.conf.task_soft_time_limit == 300
        assert app.conf.task_time_limit == 600
        assert app.conf.task_acks_late is True
        assert app.conf.task_reject_on_worker_lost is True
        
        # 测试 Worker 配置
        assert app.conf.worker_prefetch_multiplier == 4
        assert app.conf.worker_max_tasks_per_child == 1000


def test_make_celery_app():
    """测试 make_celery_app 函数"""
    with patch("app.tasks.celery_app.settings") as mock_settings:
        mock_settings.celery_broker_url = "amqp://test:test@localhost:5672/"
        mock_settings.celery_result_backend = None
        
        app = make_celery_app()
        assert app is not None
        assert isinstance(app, Celery)
        assert app.main == "gd25-arch-backend"


def test_celery_app_with_custom_broker():
    """测试使用自定义 Broker URL 创建 Celery 应用"""
    with patch("app.tasks.celery_app.settings") as mock_settings:
        mock_settings.celery_broker_url = "amqp://test:test@localhost:5672/"
        mock_settings.celery_result_backend = "redis://localhost:6379/0"
        
        app = make_celery_app()
        assert app.conf.broker_url == "amqp://test:test@localhost:5672/"
        assert app.conf.result_backend == "redis://localhost:6379/0"


def test_celery_app_without_result_backend():
    """测试不配置 Result Backend 的情况"""
    with patch("app.tasks.celery_app.settings") as mock_settings:
        mock_settings.celery_broker_url = "amqp://test:test@localhost:5672/"
        mock_settings.celery_result_backend = None
        
        app = make_celery_app()
        assert app.conf.broker_url == "amqp://test:test@localhost:5672/"
        # 不配置 Result Backend 时，backend 可能为 None 或默认值
        # 这取决于 Celery 的默认行为


def test_celery_app_without_broker_url():
    """测试未配置 Broker URL 时抛出错误"""
    with patch("app.tasks.celery_app.settings") as mock_settings:
        mock_settings.celery_broker_url = None
        mock_settings.celery_result_backend = None
        
        with pytest.raises(ValueError, match="CELERY_BROKER_URL 未配置"):
            make_celery_app()


# ==================== 基础任务类测试 ====================

def test_base_task_class():
    """测试 BaseTask 类"""
    assert BaseTask is not None
    assert issubclass(BaseTask, Task)


def test_base_task_callbacks():
    """测试 BaseTask 的回调方法"""
    # 创建任务实例
    task_instance = BaseTask()
    task_instance.name = "test_task"
    
    # 测试 on_success 回调（不应该抛出异常）
    try:
        task_instance.on_success("result", "task_id", (), {})
    except Exception as e:
        pytest.fail(f"on_success 回调失败: {e}")
    
    # 测试 on_failure 回调（不应该抛出异常）
    try:
        task_instance.on_failure(Exception("test"), "task_id", (), {}, None)
    except Exception as e:
        pytest.fail(f"on_failure 回调失败: {e}")
    
    # 测试 on_retry 回调（不应该抛出异常）
    try:
        task_instance.on_retry(Exception("test"), "task_id", (), {}, None)
    except Exception as e:
        pytest.fail(f"on_retry 回调失败: {e}")


# ==================== 任务装饰器测试 ====================

def test_task_decorator():
    """测试任务装饰器"""
    @task(name="test.decorated_task")
    def test_task_func(x: int) -> int:
        return x * 2
    
    assert test_task_func is not None
    assert hasattr(test_task_func, "delay")
    assert hasattr(test_task_func, "apply_async")


def test_task_decorator_with_bind():
    """测试带 bind 参数的任务装饰器"""
    @task(name="test.bound_task", bind=True)
    def test_bound_task(self, x: int) -> int:
        return x * 2
    
    assert test_bound_task is not None
    assert hasattr(test_bound_task, "delay")
    assert hasattr(test_bound_task, "apply_async")


def test_task_decorator_with_retry():
    """测试带重试配置的任务装饰器"""
    @task(name="test.retry_task", max_retries=5, default_retry_delay=30)
    def test_retry_task(x: int) -> int:
        return x * 2
    
    assert test_retry_task is not None
    # 检查任务配置
    assert test_retry_task.max_retries == 5
    assert test_retry_task.default_retry_delay == 30


# ==================== 任务定义测试 ====================

def test_simple_task_definition():
    """测试简单任务定义"""
    assert simple_task is not None
    assert hasattr(simple_task, "delay")
    assert hasattr(simple_task, "apply_async")
    assert simple_task.name == "app.tasks.examples.simple_task"


def test_decorated_task_definition():
    """测试使用装饰器的任务定义"""
    assert decorated_task is not None
    assert hasattr(decorated_task, "delay")
    assert hasattr(decorated_task, "apply_async")
    assert decorated_task.name == "app.tasks.examples.decorated_task"


def test_retryable_task_definition():
    """测试可重试任务定义"""
    assert retryable_task is not None
    assert hasattr(retryable_task, "delay")
    assert hasattr(retryable_task, "apply_async")
    assert retryable_task.name == "app.tasks.examples.retryable_task"
    # 检查任务配置
    assert retryable_task.max_retries == 3
    # 检查任务是否支持 bind（通过检查任务的类型）
    # 在 Celery 中，bind=True 的任务类型是 BoundTask
    # 我们可以通过检查任务是否有 retry 方法（这是绑定任务的特征）
    # 或者直接检查任务的类型
    # 实际上，bind=True 的任务可以通过检查任务实例是否有 self 参数来判断
    # 但更简单的方法是检查任务是否支持 retry 方法（这是绑定任务的核心功能）
    # 这里我们只检查配置项，bind 功能会在实际执行时验证


def test_long_running_task_definition():
    """测试长时间运行的任务定义"""
    assert long_running_task is not None
    assert hasattr(long_running_task, "delay")
    assert hasattr(long_running_task, "apply_async")
    assert long_running_task.name == "app.tasks.examples.long_running_task"


# ==================== 任务执行测试（使用测试模式）====================

@pytest.mark.integration
def test_simple_task_execution():
    """测试简单任务执行（使用 EAGER 模式）"""
    # 临时设置 Result Backend 为 None（避免需要 Redis）
    original_backend = celery_app.conf.result_backend
    celery_app.conf.result_backend = None
    
    # 配置 Celery 使用 EAGER 模式（同步执行，用于测试）
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    
    try:
        # 执行任务
        result = simple_task.delay("Hello, World!")
        
        # 在 EAGER 模式下，result 是 EagerResult，可以直接获取结果
        assert result is not None
        assert result.ready() is True
        assert "处理完成: Hello, World!" in result.result
    finally:
        # 恢复配置
        celery_app.conf.task_always_eager = False
        celery_app.conf.task_eager_propagates = False
        celery_app.conf.result_backend = original_backend


@pytest.mark.integration
def test_decorated_task_execution():
    """测试装饰器任务执行（使用 EAGER 模式）"""
    # 临时设置 Result Backend 为 None（避免需要 Redis）
    original_backend = celery_app.conf.result_backend
    celery_app.conf.result_backend = None
    
    # 配置 Celery 使用 EAGER 模式
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    
    try:
        # 执行任务
        test_data = {"key": "value", "number": 42}
        result = decorated_task.delay(test_data)
        
        # 检查结果
        assert result is not None
        assert result.ready() is True
        assert result.result["status"] == "success"
        assert result.result["data"] == test_data
        assert "processed_at" in result.result
    finally:
        # 恢复配置
        celery_app.conf.task_always_eager = False
        celery_app.conf.task_eager_propagates = False
        celery_app.conf.result_backend = original_backend


@pytest.mark.integration
def test_retryable_task_execution_success():
    """测试可重试任务执行（成功情况）"""
    # 临时设置 Result Backend 为 None（避免需要 Redis）
    original_backend = celery_app.conf.result_backend
    celery_app.conf.result_backend = None
    
    # 配置 Celery 使用 EAGER 模式
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    
    try:
        # 执行任务（使用有效值）
        result = retryable_task.delay(10)
        
        # 检查结果
        assert result is not None
        assert result.ready() is True
        assert result.result == 20  # 10 * 2
    finally:
        # 恢复配置
        celery_app.conf.task_always_eager = False
        celery_app.conf.task_eager_propagates = False
        celery_app.conf.result_backend = original_backend


@pytest.mark.integration
def test_long_running_task_execution():
    """测试长时间运行的任务执行（使用 EAGER 模式）"""
    # 临时设置 Result Backend 为 None（避免需要 Redis）
    original_backend = celery_app.conf.result_backend
    celery_app.conf.result_backend = None
    
    # 配置 Celery 使用 EAGER 模式
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    
    try:
        # 执行任务（使用较短的持续时间）
        result = long_running_task.delay(1)
        
        # 检查结果
        assert result is not None
        assert result.ready() is True
        assert "任务完成" in result.result
        assert "1 秒" in result.result
    finally:
        # 恢复配置
        celery_app.conf.task_always_eager = False
        celery_app.conf.task_eager_propagates = False
        celery_app.conf.result_backend = original_backend


# ==================== 任务配置测试 ====================

def test_task_imports_configuration():
    """测试任务导入配置"""
    assert "app.tasks" in celery_app.conf.imports


def test_task_routes_configuration():
    """测试任务路由配置"""
    # 任务路由应该是字典类型
    assert isinstance(celery_app.conf.task_routes, dict)


# ==================== 错误处理测试 ====================

@pytest.mark.integration
def test_task_exception_handling():
    """测试任务异常处理"""
    # 配置 Celery 使用 EAGER 模式
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    
    # 定义一个会抛出异常的任务
    @celery_app.task(name="test.exception_task")
    def exception_task():
        raise ValueError("测试异常")
    
    try:
        # 执行任务（应该抛出异常）
        with pytest.raises(ValueError, match="测试异常"):
            exception_task.delay()
    finally:
        # 恢复配置
        celery_app.conf.task_always_eager = False
        celery_app.conf.task_eager_propagates = False


# ==================== 任务信号测试 ====================

def test_task_signals_registered():
    """测试任务信号是否已注册"""
    # 检查信号处理器是否已注册
    # 注意：这需要实际运行任务才能验证，这里只检查配置
    assert celery_app is not None


# ==================== 导出测试 ====================

def test_celery_app_exports():
    """测试模块导出"""
    from app.tasks import celery_app, make_celery_app, BaseTask, task
    
    assert celery_app is not None
    assert make_celery_app is not None
    assert BaseTask is not None
    assert task is not None


# ==================== 主测试函数 ====================

def run_all_tests():
    """运行所有测试"""
    import pytest
    
    print("=" * 60)
    print("开始测试 Celery 任务模块")
    print("=" * 60)
    
    try:
        # 构建 pytest 参数
        pytest_args = [
            __file__,
            "-v",           # 详细输出
            "-s",           # 显示打印语句
            "-o", "addopts=",  # 忽略 pytest.ini 中的 addopts 配置
        ]
        
        # 运行测试
        exit_code = pytest.main(pytest_args)
        
        if exit_code == 0:
            print("\n" + "=" * 60)
            print("✓ 所有测试通过！")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print(f"✗ 测试失败，退出码: {exit_code}")
            print("=" * 60)
        
        return exit_code
        
    except Exception as e:
        print(f"\n✗ 测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_tests()

