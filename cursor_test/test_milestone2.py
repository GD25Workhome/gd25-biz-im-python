#!/usr/bin/env python
"""
里程碑2测试脚本

测试数据模型、Schema和Repository的实现。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置占位符环境变量（如果未设置）
if not os.getenv("AI_SERVICE_URL"):
    os.environ["AI_SERVICE_URL"] = "http://placeholder.ai"
if not os.getenv("AI_SERVICE_API_KEY"):
    os.environ["AI_SERVICE_API_KEY"] = "placeholder_key"

from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.utils.id_generator import generate_user_id, generate_group_id, generate_message_id
from app.repositories.user_repository import UserRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.group_member_repository import GroupMemberRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.user import UserCreate, UserResponse
from app.schemas.group import GroupCreate, GroupResponse
from app.schemas.message import MessageCreate, MessageResponse


def test_imports():
    """测试所有模块是否可以正常导入"""
    print("=" * 60)
    print("测试 1: 模块导入")
    print("=" * 60)
    
    try:
        # 测试模型导入
        from app.models import User, Group, GroupMember, Message
        print("✓ 模型导入成功")
        
        # 测试 Schema 导入
        from app.schemas import (
            UserCreate, UserUpdate, UserResponse,
            GroupCreate, GroupResponse, GroupMemberAdd,
            MessageCreate, MessageResponse, MessageListResponse
        )
        print("✓ Schema 导入成功")
        
        # 测试 Repository 导入
        from app.repositories import (
            UserRepository, GroupRepository,
            GroupMemberRepository, MessageRepository
        )
        print("✓ Repository 导入成功")
        
        # 测试 ID 生成器导入
        from app.utils.id_generator import (
            generate_user_id, generate_group_id, generate_message_id
        )
        print("✓ ID 生成器导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schemas():
    """测试 Schema 验证"""
    print("\n" + "=" * 60)
    print("测试 2: Schema 验证")
    print("=" * 60)
    
    try:
        # 测试 UserCreate
        user_create = UserCreate(username="测试用户", user_role="PATIENT")
        print(f"✓ UserCreate 验证成功: {user_create.username}, {user_create.user_role}")
        
        # 测试 GroupCreate
        group_create = GroupCreate(group_name="测试群组", description="测试描述")
        print(f"✓ GroupCreate 验证成功: {group_create.group_name}")
        
        # 测试 MessageCreate
        message_create = MessageCreate(group_id="group_001", content="测试消息")
        print(f"✓ MessageCreate 验证成功: {message_create.content}")
        
        # 测试无效数据（应该失败）
        try:
            invalid_user = UserCreate(username="", user_role="INVALID")
            print("✗ UserCreate 应该拒绝空用户名")
            return False
        except Exception:
            print("✓ UserCreate 正确拒绝了无效数据")
        
        return True
    except Exception as e:
        print(f"✗ Schema 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_repositories():
    """测试 Repository CRUD 操作"""
    print("\n" + "=" * 60)
    print("测试 3: Repository CRUD 操作")
    print("=" * 60)
    
    db: Session = None
    try:
        # 获取数据库会话
        db = get_db_session()
        
        # 测试 UserRepository
        print("\n--- 测试 UserRepository ---")
        user_repo = UserRepository(db)
        user_id = generate_user_id()
        user = user_repo.create(user_id, "测试用户", "PATIENT")
        print(f"✓ 创建用户成功: {user.user_id}")
        
        found_user = user_repo.get_by_id(user_id)
        if found_user and found_user.user_id == user_id:
            print(f"✓ 查询用户成功: {found_user.username}")
        else:
            print("✗ 查询用户失败")
            return False
        
        # 测试 GroupRepository
        print("\n--- 测试 GroupRepository ---")
        group_repo = GroupRepository(db)
        group_id = generate_group_id()
        group = group_repo.create(group_id, "测试群组", "测试描述", user_id)
        print(f"✓ 创建群组成功: {group.group_id}")
        
        found_group = group_repo.get_by_id(group_id)
        if found_group and found_group.group_id == group_id:
            print(f"✓ 查询群组成功: {found_group.group_name}")
        else:
            print("✗ 查询群组失败")
            return False
        
        # 测试 GroupMemberRepository
        print("\n--- 测试 GroupMemberRepository ---")
        member_repo = GroupMemberRepository(db)
        member = member_repo.add_member(group_id, user_id, "DOCTOR")
        print(f"✓ 添加成员成功: {member.user_id}")
        
        found_member = member_repo.get_member(group_id, user_id)
        if found_member:
            print(f"✓ 查询成员成功: {found_member.user_role}")
        else:
            print("✗ 查询成员失败")
            return False
        
        members = member_repo.get_members_by_group(group_id)
        print(f"✓ 查询群组所有成员成功: {len(members)} 个成员")
        
        # 测试 MessageRepository
        print("\n--- 测试 MessageRepository ---")
        message_repo = MessageRepository(db)
        message_id = generate_message_id()
        message = message_repo.create(
            message_id, group_id, user_id, "TEXT", "这是一条测试消息"
        )
        print(f"✓ 创建消息成功: {message.message_id}")
        
        found_message = message_repo.get_by_id(message_id)
        if found_message and found_message.message_id == message_id:
            print(f"✓ 查询消息成功: {found_message.msg_content}")
        else:
            print("✗ 查询消息失败")
            return False
        
        messages, total = message_repo.get_by_group(group_id, page=1, page_size=10)
        print(f"✓ 分页查询消息成功: {len(messages)} 条消息，共 {total} 条")
        
        # 清理测试数据
        print("\n--- 清理测试数据 ---")
        message_repo.db.delete(found_message)
        member_repo.remove_member(group_id, user_id)
        group_repo.db.delete(found_group)
        user_repo.db.delete(found_user)
        db.commit()
        print("✓ 测试数据清理完成")
        
        return True
    except Exception as e:
        print(f"✗ Repository 测试失败: {e}")
        import traceback
        traceback.print_exc()
        if db:
            db.rollback()
        return False
    finally:
        if db:
            db.close()


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("里程碑2 - 测试验证")
    print("=" * 60)
    
    results = []
    
    # 测试1: 模块导入
    results.append(("模块导入", test_imports()))
    
    # 测试2: Schema 验证
    results.append(("Schema 验证", test_schemas()))
    
    # 测试3: Repository CRUD
    results.append(("Repository CRUD", test_repositories()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！里程碑2实现正确。")
    else:
        print("\n⚠️  部分测试失败，请检查实现。")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
