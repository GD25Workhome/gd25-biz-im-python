# Alembic 数据库迁移

此目录包含数据库迁移脚本。

## 使用说明

### 创建迁移脚本

```bash
# 自动生成迁移脚本（基于模型变更）
alembic revision --autogenerate -m "描述信息"

# 创建空迁移脚本
alembic revision -m "描述信息"
```

### 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision_id>

# 降级一个版本
alembic downgrade -1

# 降级到指定版本
alembic downgrade <revision_id>
```

### 查看迁移历史

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 查看迁移历史（详细）
alembic history --verbose
```

## 注意事项

1. 迁移脚本会自动检测模型变更，但建议仔细检查生成的脚本
2. 在生产环境执行迁移前，请先备份数据库
3. 迁移脚本应该包含升级和降级两个方向的逻辑

