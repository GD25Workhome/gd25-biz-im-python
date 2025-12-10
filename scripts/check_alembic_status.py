#!/usr/bin/env python
"""
检查 Alembic 和数据库状态脚本

功能：
- 检查数据库连接
- 检查数据库中的表
- 检查 Alembic 版本表
- 检查迁移脚本状态

使用方式：
    python scripts/check_alembic_status.py
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置占位符环境变量（如果未设置）
if not os.getenv("AI_SERVICE_URL"):
    os.environ["AI_SERVICE_URL"] = "http://placeholder.ai"
if not os.getenv("AI_SERVICE_API_KEY"):
    os.environ["AI_SERVICE_API_KEY"] = "placeholder_key"

from app.config import settings


def check_database_status():
    """检查数据库状态"""
    print("=" * 60)
    print("数据库状态检查")
    print("=" * 60)
    
    try:
        # 获取数据库 URL
        database_url = settings.get_database_url_sync(allow_placeholder=False)
        print(f"\n数据库 URL: {database_url.split('@')[1] if '@' in database_url else '已配置'}")
        
        print(f"\n正在连接数据库...")
        engine = create_engine(database_url)
        
        # 创建检查器
        inspector = inspect(engine)
        
        # 获取所有表名
        existing_tables = inspector.get_table_names()
        
        print(f"\n数据库中的表（共 {len(existing_tables)} 个）：")
        if existing_tables:
            for table in sorted(existing_tables):
                print(f"  - {table}")
        else:
            print("  （空数据库，无任何表）")
        
        # 检查 alembic_version 表
        print(f"\n检查 Alembic 版本表...")
        if 'alembic_version' in existing_tables:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                if version:
                    print(f"  ✓ alembic_version 表存在")
                    print(f"  当前版本: {version}")
                else:
                    print(f"  ⚠ alembic_version 表存在但为空")
        else:
            print(f"  ✗ alembic_version 表不存在（数据库未初始化）")
        
        # 检查必需的表
        required_tables = [
            "users",
            "groups",
            "group_members",
            "messages",
            "ai_interaction_records",
        ]
        
        print(f"\n检查必需的业务表...")
        missing_tables = []
        for table_name in required_tables:
            if table_name in existing_tables:
                columns = inspector.get_columns(table_name)
                indexes = inspector.get_indexes(table_name)
                print(f"  ✓ {table_name} - 存在 ({len(columns)} 个字段, {len(indexes)} 个索引)")
            else:
                print(f"  ✗ {table_name} - 不存在")
                missing_tables.append(table_name)
        
        engine.dispose()
        
        return {
            'connected': True,
            'tables': existing_tables,
            'has_alembic_version': 'alembic_version' in existing_tables,
            'missing_tables': missing_tables,
            'is_empty': len(existing_tables) == 0
        }
        
    except ValueError as e:
        print(f"\n✗ 配置错误: {e}")
        print(f"  请设置 DATABASE_URL 环境变量或在 .env 文件中配置")
        return {'connected': False, 'error': str(e)}
    except OperationalError as e:
        print(f"\n✗ 数据库连接失败: {e}")
        print(f"  请检查数据库 URL 配置是否正确，数据库是否正在运行")
        return {'connected': False, 'error': str(e)}
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return {'connected': False, 'error': str(e)}


def check_alembic_migrations():
    """检查 Alembic 迁移脚本"""
    print("\n" + "=" * 60)
    print("Alembic 迁移脚本检查")
    print("=" * 60)
    
    versions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alembic', 'versions')
    
    if not os.path.exists(versions_dir):
        print(f"\n✗ 迁移脚本目录不存在: {versions_dir}")
        return []
    
    migration_files = [f for f in os.listdir(versions_dir) if f.endswith('.py') and f != '__init__.py']
    
    print(f"\n迁移脚本文件（共 {len(migration_files)} 个）：")
    for f in sorted(migration_files):
        print(f"  - {f}")
    
    return migration_files


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Alembic 和数据库状态检查")
    print("=" * 60)
    
    # 检查数据库状态
    db_status = check_database_status()
    
    # 检查迁移脚本
    migration_files = check_alembic_migrations()
    
    # 给出建议
    print("\n" + "=" * 60)
    print("建议")
    print("=" * 60)
    
    if not db_status.get('connected'):
        print("\n✗ 无法连接到数据库，请先检查数据库配置")
        return
    
    if db_status.get('is_empty'):
        print("\n✓ 数据库为空，这是新数据库")
        print("\n建议执行以下命令初始化数据库：")
        print("  1. alembic upgrade head")
        print("     （这会在空数据库中创建所有表并设置 Alembic 版本）")
    elif db_status.get('has_alembic_version'):
        current_version = db_status.get('current_version', '未知')
        print(f"\n✓ 数据库已初始化，当前 Alembic 版本: {current_version}")
        if db_status.get('missing_tables'):
            print(f"\n⚠ 缺少以下表: {', '.join(db_status['missing_tables'])}")
            print("  建议执行: alembic upgrade head")
        else:
            print("\n✓ 所有必需的表都已存在")
    else:
        print("\n⚠ 数据库中有表，但没有 alembic_version 表")
        print("  这可能意味着：")
        print("  1. 数据库是通过其他方式创建的（非 Alembic）")
        print("  2. alembic_version 表被删除了")
        print("\n  建议：")
        print("  选项 A: 如果表结构正确，可以手动创建 alembic_version 表并插入当前版本")
        print("  选项 B: 如果表结构不正确，可以删除所有表后执行: alembic upgrade head")
    
    if migration_files:
        print(f"\n✓ 找到 {len(migration_files)} 个迁移脚本文件")
        print("  迁移脚本文件不需要重新生成，可以直接使用")
    else:
        print("\n⚠ 没有找到迁移脚本文件")
        print("  需要生成初始迁移脚本: alembic revision --autogenerate -m 'create_initial_tables'")


if __name__ == "__main__":
    main()
