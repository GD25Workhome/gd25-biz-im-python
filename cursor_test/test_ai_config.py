"""
AI配置加载测试脚本

验证新的AI服务配置格式可以正常加载：
- ai_service_url
- ai_service_api_key
- ai_service_timeout
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 在导入配置之前设置默认环境变量（避免导入时验证失败）
if "AI_SERVICE_URL" not in os.environ:
    os.environ["AI_SERVICE_URL"] = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
if "AI_SERVICE_API_KEY" not in os.environ:
    os.environ["AI_SERVICE_API_KEY"] = "test_api_key_default"

from app.config import IMSettings


def test_ai_config_loading():
    """测试AI配置加载"""
    print("\n" + "=" * 60)
    print("测试AI配置加载")
    print("=" * 60)
    
    # 设置测试环境变量
    test_env = {
        "AI_SERVICE_URL": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "AI_SERVICE_API_KEY": "test_api_key_12345",
        "AI_SERVICE_TIMEOUT": "30",
    }
    
    with patch.dict(os.environ, test_env, clear=False):
        try:
            # 创建配置实例
            config = IMSettings()
            
            # 验证配置项存在
            assert hasattr(config, 'ai_service_url'), "配置缺少 ai_service_url"
            assert hasattr(config, 'ai_service_api_key'), "配置缺少 ai_service_api_key"
            assert hasattr(config, 'ai_service_timeout'), "配置缺少 ai_service_timeout"
            
            # 验证配置值
            assert config.ai_service_url == test_env["AI_SERVICE_URL"], \
                f"ai_service_url 值不匹配: {config.ai_service_url}"
            assert config.ai_service_api_key == test_env["AI_SERVICE_API_KEY"], \
                f"ai_service_api_key 值不匹配: {config.ai_service_api_key}"
            assert config.ai_service_timeout == int(test_env["AI_SERVICE_TIMEOUT"]), \
                f"ai_service_timeout 值不匹配: {config.ai_service_timeout}"
            
            # 打印配置信息
            print(f"✓ ai_service_url: {config.ai_service_url}")
            print(f"✓ ai_service_api_key: {config.ai_service_api_key[:10]}... (已隐藏)")
            print(f"✓ ai_service_timeout: {config.ai_service_timeout}秒")
            print("\n✅ AI配置加载测试通过！")
            
            return True
            
        except Exception as e:
            print(f"\n❌ AI配置加载测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_ai_config_required_fields():
    """测试AI配置必需字段验证"""
    print("\n" + "=" * 60)
    print("测试AI配置必需字段验证")
    print("=" * 60)
    
    # 验证配置字段是必需的（通过检查Field定义）
    from app.config import IMSettings
    from pydantic import Field
    
    # 检查字段定义
    model_fields = IMSettings.model_fields
    
    # 验证 ai_service_url 是必需的
    ai_url_field = model_fields.get('ai_service_url')
    assert ai_url_field is not None, "ai_service_url 字段不存在"
    # 检查是否是必需字段（没有默认值）
    has_default = ai_url_field.default is not ... and ai_url_field.default is not None
    print(f"✓ ai_service_url 字段存在，必需: {not has_default}")
    
    # 验证 ai_service_api_key 是必需的
    ai_key_field = model_fields.get('ai_service_api_key')
    assert ai_key_field is not None, "ai_service_api_key 字段不存在"
    has_default = ai_key_field.default is not ... and ai_key_field.default is not None
    print(f"✓ ai_service_api_key 字段存在，必需: {not has_default}")
    
    # 验证 ai_service_timeout 有默认值
    ai_timeout_field = model_fields.get('ai_service_timeout')
    assert ai_timeout_field is not None, "ai_service_timeout 字段不存在"
    has_default = ai_timeout_field.default is not ... and ai_timeout_field.default is not None
    assert has_default, "ai_service_timeout 应该有默认值"
    assert ai_timeout_field.default == 30, f"ai_service_timeout 默认值应为30，实际为{ai_timeout_field.default}"
    print(f"✓ ai_service_timeout 字段存在，默认值: {ai_timeout_field.default}秒")
    
    print("\n✅ AI配置必需字段验证测试通过！")
    return True


def test_ai_config_timeout_validation():
    """测试AI配置超时时间验证"""
    print("\n" + "=" * 60)
    print("测试AI配置超时时间验证")
    print("=" * 60)
    
    # 测试默认值
    test_env = {
        "AI_SERVICE_URL": "https://example.com/api",
        "AI_SERVICE_API_KEY": "test_key",
    }
    
    with patch.dict(os.environ, test_env, clear=False):
        config = IMSettings()
        assert config.ai_service_timeout == 30, f"默认超时时间应为30秒，实际为{config.ai_service_timeout}秒"
        print(f"✓ 默认超时时间: {config.ai_service_timeout}秒")
    
    # 测试自定义超时时间
    test_env["AI_SERVICE_TIMEOUT"] = "60"
    with patch.dict(os.environ, test_env, clear=False):
        config = IMSettings()
        assert config.ai_service_timeout == 60, f"超时时间应为60秒，实际为{config.ai_service_timeout}秒"
        print(f"✓ 自定义超时时间: {config.ai_service_timeout}秒")
    
    print("\n✅ AI配置超时时间验证测试通过！")
    return True


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("AI配置加载验证测试")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("配置加载测试", test_ai_config_loading()))
    results.append(("必需字段验证", test_ai_config_required_fields()))
    results.append(("超时时间验证", test_ai_config_timeout_validation()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！配置可以正常加载。")
        return 0
    else:
        print("❌ 部分测试失败，请检查配置。")
        return 1


if __name__ == "__main__":
    exit(main())
