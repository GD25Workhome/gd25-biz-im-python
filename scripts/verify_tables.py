#!/usr/bin/env python
"""
验证数据库表创建脚本

功能：
- 检查所有必需的表是否存在
- 验证表结构是否正确

使用方式：
    python scripts/verify_tables.py
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置占位符环境变量（如果未设置）
if not os.getenv("AI_SERVICE_URL"):
    os.environ["AI_SERVICE_URL"] = "http://placeholder.ai"
if not os.getenv("AI_SERVICE_API_KEY"):
    os.environ["AI_SERVICE_API_KEY"] = "placeholder_key"

from app.config import settings


def verify_tables() -> bool:
    """
    验证所有必需的表是否存在
    
    Returns:
        bool: 所有表都存在返回 True，否则返回 False
    """
    # 必需的表格列表
    required_tables = [
        "users",
        "groups",
        "group_members",
        "messages",
        "ai_interaction_records",
    ]
    
    try:
        # 获取数据库 URL
        database_url = settings.get_database_url_sync(allow_placeholder=False)
        
        print(f"正在连接数据库...")
        engine = create_engine(database_url)
        
        # 创建检查器
        inspector = inspect(engine)
        
        # 获取所有表名
        existing_tables = inspector.get_table_names()
        
        print(f"\n数据库中的表：{', '.join(existing_tables) if existing_tables else '无'}")
        print(f"\n检查必需的表...")
        
        all_exist = True
        for table_name in required_tables:
            if table_name in existing_tables:
                print(f"  ✓ {table_name} - 存在")
            else:
                print(f"  ✗ {table_name} - 不存在")
                all_exist = False
        
        if all_exist:
            print(f"\n✓ 所有必需的表都已创建！")
            
            # 验证表结构（可选）
            print(f"\n验证表结构...")
            for table_name in required_tables:
                columns = inspector.get_columns(table_name)
                indexes = inspector.get_indexes(table_name)
                print(f"  {table_name}: {len(columns)} 个字段, {len(indexes)} 个索引")
            
            engine.dispose()
            return True
        else:
            print(f"\n✗ 部分表缺失，请执行数据库迁移：")
            print(f"  alembic upgrade head")
            engine.dispose()
            return False
            
    except ValueError as e:
        print(f"✗ 配置错误: {e}")
        print(f"  请设置 DATABASE_URL 环境变量或在 .env 文件中配置")
        return False
    except OperationalError as e:
        print(f"✗ 数据库连接失败: {e}")
        print(f"  请检查数据库 URL 配置是否正确，数据库是否正在运行")
        return False
    except Exception as e:
        print(f"✗ 发生错误: {e}")
        return False


if __name__ == "__main__":
    success = verify_tables()
    sys.exit(0 if success else 1)
