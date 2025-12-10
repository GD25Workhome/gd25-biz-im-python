#!/usr/bin/env python
"""
数据库初始化脚本

功能：
- 自动创建数据库（如果不存在）
- 验证数据库连接
- 可选安装 PostgreSQL pgvector 扩展

使用方式：
    python scripts/init_db.py
    python scripts/init_db.py --install-pgvector
"""

import argparse
import sys
import os
from urllib.parse import urlparse, urlunparse
from typing import Optional, Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


def parse_database_url(database_url: str) -> Tuple[str, str, str, str, str, str]:
    """
    解析数据库 URL，返回各个组件
    
    Args:
        database_url: 数据库连接 URL
        
    Returns:
        Tuple[scheme, netloc, path, params, query, fragment]
    """
    parsed = urlparse(database_url)
    return (
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    )


def get_server_url(database_url: str) -> str:
    """
    从数据库 URL 中提取服务器连接 URL（不包含数据库名）
    
    Args:
        database_url: 完整的数据库连接 URL
        
    Returns:
        服务器连接 URL（连接到默认数据库 postgres 或 mysql）
    """
    scheme, netloc, path, params, query, fragment = parse_database_url(database_url)
    
    # 移除路径中的数据库名，连接到默认数据库
    if scheme.startswith("postgresql"):
        # PostgreSQL: 连接到 postgres 数据库
        new_path = "/postgres"
    elif scheme.startswith("mysql"):
        # MySQL: 连接到 mysql 数据库
        new_path = "/mysql"
    else:
        raise ValueError(f"不支持的数据库类型: {scheme}")
    
    return urlunparse((scheme, netloc, new_path, params, query, fragment))


def get_database_name(database_url: str) -> str:
    """
    从数据库 URL 中提取数据库名
    
    Args:
        database_url: 完整的数据库连接 URL
        
    Returns:
        数据库名
    """
    _, _, path, _, _, _ = parse_database_url(database_url)
    # 移除前导斜杠
    db_name = path.lstrip("/")
    if not db_name:
        raise ValueError("数据库 URL 中未指定数据库名")
    return db_name


def is_postgresql(database_url: str) -> bool:
    """判断是否为 PostgreSQL 数据库"""
    scheme, _, _, _, _, _ = parse_database_url(database_url)
    return scheme.startswith("postgresql")


def is_mysql(database_url: str) -> bool:
    """判断是否为 MySQL 数据库"""
    scheme, _, _, _, _, _ = parse_database_url(database_url)
    return scheme.startswith("mysql")


def create_database(database_url: str) -> bool:
    """
    创建数据库（如果不存在）
    
    Args:
        database_url: 完整的数据库连接 URL
        
    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        db_name = get_database_name(database_url)
        server_url = get_server_url(database_url)
        
        print(f"正在连接到数据库服务器: {server_url}")
        print(f"目标数据库: {db_name}")
        
        # 连接到服务器（而非特定数据库）
        engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            if is_postgresql(database_url):
                # PostgreSQL: 检查数据库是否存在
                result = conn.execute(
                    text(
                        "SELECT 1 FROM pg_database WHERE datname = :db_name"
                    ),
                    {"db_name": db_name}
                )
                exists = result.fetchone() is not None
                
                if exists:
                    print(f"✓ 数据库 '{db_name}' 已存在")
                    return True
                
                # 创建数据库
                print(f"正在创建数据库 '{db_name}'...")
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                print(f"✓ 数据库 '{db_name}' 创建成功")
                
            elif is_mysql(database_url):
                # MySQL: 检查数据库是否存在
                result = conn.execute(
                    text("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db_name"),
                    {"db_name": db_name}
                )
                exists = result.fetchone() is not None
                
                if exists:
                    print(f"✓ 数据库 '{db_name}' 已存在")
                    return True
                
                # 创建数据库
                print(f"正在创建数据库 '{db_name}'...")
                conn.execute(text(f"CREATE DATABASE `{db_name}`"))
                print(f"✓ 数据库 '{db_name}' 创建成功")
            else:
                print(f"✗ 不支持的数据库类型")
                return False
        
        engine.dispose()
        return True
        
    except OperationalError as e:
        print(f"✗ 数据库连接失败: {e}")
        print("  请检查：")
        print("  1. 数据库服务器是否已启动")
        print("  2. 连接信息是否正确（用户名、密码、主机、端口）")
        print("  3. 用户是否有创建数据库的权限")
        return False
    except ProgrammingError as e:
        print(f"✗ 创建数据库失败: {e}")
        print("  可能原因：权限不足或数据库已存在")
        return False
    except Exception as e:
        print(f"✗ 发生未知错误: {e}")
        return False


def check_database_connection(database_url: str) -> bool:
    """
    验证数据库连接
    
    Args:
        database_url: 完整的数据库连接 URL
        
    Returns:
        bool: 连接成功返回 True，否则返回 False
    """
    try:
        print(f"正在验证数据库连接...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✓ 数据库连接验证成功")
                engine.dispose()
                return True
            else:
                print("✗ 数据库连接验证失败")
                engine.dispose()
                return False
                
    except OperationalError as e:
        print(f"✗ 数据库连接失败: {e}")
        print("  请检查数据库 URL 配置是否正确")
        return False
    except Exception as e:
        print(f"✗ 验证连接时发生错误: {e}")
        return False


def check_pgvector_extension(database_url: str) -> bool:
    """
    检查 pgvector 扩展是否已安装
    
    Args:
        database_url: 完整的数据库连接 URL
        
    Returns:
        bool: 已安装返回 True，否则返回 False
    """
    if not is_postgresql(database_url):
        return False
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            exists = result.fetchone() is not None
            engine.dispose()
            return exists
    except Exception:
        return False


def install_pgvector_extension(database_url: str) -> bool:
    """
    安装 pgvector 扩展
    
    Args:
        database_url: 完整的数据库连接 URL
        
    Returns:
        bool: 安装成功返回 True，否则返回 False
    """
    if not is_postgresql(database_url):
        print("✗ pgvector 扩展仅支持 PostgreSQL 数据库")
        return False
    
    # 检查是否已安装
    if check_pgvector_extension(database_url):
        print("✓ pgvector 扩展已安装")
        return True
    
    try:
        print("正在安装 pgvector 扩展...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # 需要超级用户权限或数据库所有者权限
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        
        engine.dispose()
        
        # 验证安装
        if check_pgvector_extension(database_url):
            print("✓ pgvector 扩展安装成功")
            return True
        else:
            print("✗ pgvector 扩展安装失败（验证时未找到扩展）")
            return False
            
    except ProgrammingError as e:
        print(f"✗ 安装 pgvector 扩展失败: {e}")
        print("  可能原因：")
        print("  1. 用户没有安装扩展的权限（需要超级用户或数据库所有者权限）")
        print("  2. pgvector 扩展未在 PostgreSQL 服务器上安装")
        print("  3. 需要先安装 pgvector 扩展到 PostgreSQL 服务器")
        print("     Ubuntu/Debian: sudo apt-get install postgresql-14-pgvector")
        print("     或从源码编译安装: https://github.com/pgvector/pgvector")
        return False
    except Exception as e:
        print(f"✗ 安装 pgvector 扩展时发生错误: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="数据库初始化脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 仅创建数据库
  python scripts/init_db.py
  
  # 创建数据库并安装 pgvector 扩展
  python scripts/init_db.py --install-pgvector
        """
    )
    parser.add_argument(
        "--install-pgvector",
        action="store_true",
        help="安装 PostgreSQL pgvector 扩展（仅支持 PostgreSQL）"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("数据库初始化脚本")
    print("=" * 60)
    print()
    
    # 验证数据库配置
    try:
        settings.validate_database_config()
    except ValueError as e:
        print(f"✗ 配置错误: {e}")
        print()
        print("请设置环境变量 DATABASE_URL 或在 .env 文件中配置。")
        print("示例：")
        print("  DATABASE_URL=postgresql://user:password@localhost:5432/dbname")
        print("  DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname")
        sys.exit(1)
    
    database_url = settings.database_url
    assert database_url is not None  # 已验证配置
    
    print(f"数据库类型: {'PostgreSQL' if is_postgresql(database_url) else 'MySQL' if is_mysql(database_url) else '未知'}")
    print()
    
    # 步骤 1: 创建数据库
    print("步骤 1: 创建数据库")
    print("-" * 60)
    if not create_database(database_url):
        print()
        print("数据库初始化失败，请检查错误信息并重试。")
        sys.exit(1)
    print()
    
    # 步骤 2: 验证连接
    print("步骤 2: 验证数据库连接")
    print("-" * 60)
    if not check_database_connection(database_url):
        print()
        print("数据库连接验证失败，请检查错误信息并重试。")
        sys.exit(1)
    print()
    
    # 步骤 3: 安装 pgvector 扩展（可选）
    if args.install_pgvector:
        print("步骤 3: 安装 pgvector 扩展")
        print("-" * 60)
        if not install_pgvector_extension(database_url):
            print()
            print("⚠️  pgvector 扩展安装失败，但不影响数据库初始化。")
            print("   你可以稍后手动安装扩展，或使用具有足够权限的用户重试。")
            print()
        else:
            print()
    
    # 完成
    print("=" * 60)
    print("✓ 数据库初始化完成！")
    print("=" * 60)
    print()
    print("下一步：")
    print("  1. 运行数据库迁移: alembic upgrade head")
    print("  2. 启动应用: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
