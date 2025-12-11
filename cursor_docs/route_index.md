# FastAPI 路由索引

> 本文档由 `scripts/generate_route_index.py` 自动生成

## 路由映射表

### group.py (/api)

| HTTP 方法 | URL 路径 | 完整路径 | 函数名 | 行号 |
|----------|---------|---------|--------|------|
| POST | `/group/create` | `/api/group/create` | `create_group` | [38](../app/api/group.py#L38) |
| GET | `/group/{group_id}` | `/api/group/{group_id}` | `get_group` | [94](../app/api/group.py#L94) |
| POST | `/group/{group_id}/members` | `/api/group/{group_id}/members` | `add_member` | [130](../app/api/group.py#L130) |
| GET | `/group/{group_id}/members` | `/api/group/{group_id}/members` | `get_group_members` | [184](../app/api/group.py#L184) |

### main.py ()

| HTTP 方法 | URL 路径 | 完整路径 | 函数名 | 行号 |
|----------|---------|---------|--------|------|
| GET | `/health` | `/health` | `health_check` | [251](../app/main.py#L251) |
| GET | `/version` | `/version` | `get_version` | [279](../app/main.py#L279) |
| GET | `/ws/stats` | `/ws/stats` | `websocket_stats` | [344](../app/main.py#L344) |

### user.py (/api)

| HTTP 方法 | URL 路径 | 完整路径 | 函数名 | 行号 |
|----------|---------|---------|--------|------|
| POST | `/user/create` | `/api/user/create` | `create_user` | [47](../app/api/user.py#L47) |
| GET | `/user/{user_id}` | `/api/user/{user_id}` | `get_user` | [94](../app/api/user.py#L94) |
| PUT | `/user/{user_id}/role` | `/api/user/{user_id}/role` | `update_user_role` | [130](../app/api/user.py#L130) |

### users.py (/api)

| HTTP 方法 | URL 路径 | 完整路径 | 函数名 | 行号 |
|----------|---------|---------|--------|------|
| POST | `/` | `/api/` | `create_user` | [44](../app/api/users.py#L44) |
| GET | `/{user_id}` | `/api/{user_id}` | `get_user` | [72](../app/api/users.py#L72) |
| PUT | `/{user_id}` | `/api/{user_id}` | `update_user` | [99](../app/api/users.py#L99) |
| DELETE | `/{user_id}` | `/api/{user_id}` | `delete_user` | [128](../app/api/users.py#L128) |
| GET | `/` | `/api/` | `get_users` | [153](../app/api/users.py#L153) |
| GET | `/search` | `/api/search` | `search_users` | [200](../app/api/users.py#L200) |

## 快速查找技巧

### 在 Cursor/VSCode 中：

1. **全局搜索**：`Cmd + Shift + F`（Mac）或 `Ctrl + Shift + F`（Windows/Linux）
   - 搜索 URL 路径（如 `/user/create`）

2. **符号搜索**：`Cmd + Shift + O`（Mac）或 `Ctrl + Shift + O`（Windows/Linux）
   - 搜索函数名（如 `create_user`）

3. **文件内搜索**：`Cmd + F`（Mac）或 `Ctrl + F`（Windows/Linux）
   - 在当前文件中搜索路径字符串

4. **Go to Definition**：`Cmd + Click`（Mac）或 `Ctrl + Click`（Windows/Linux）
   - 点击路由路径字符串，可以跳转到定义

### 路由注册位置

所有业务路由在 `app/main.py` 中注册。

## 更新说明

运行以下命令更新此索引：
```bash
python scripts/generate_route_index.py
```
