# 测试数据库连接
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.database import engine
from app.db.session import SessionLocal
from app.db.base import Base

# 测试连接
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    assert result.scalar() == 1
    print("✓ 数据库连接测试通过")

# 测试会话
db = SessionLocal()
try:
    # 测试查询
    result = db.execute(text("SELECT 1"))
    assert result.scalar() == 1
    print("✓ 数据库会话测试通过")
finally:
    db.close()