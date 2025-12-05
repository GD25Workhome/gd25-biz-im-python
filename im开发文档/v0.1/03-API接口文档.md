# 轻量级 IM 服务 - API 接口文档

## 一、API 概述

### 1.1 基础信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: v1
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2 认证方式

当前版本简化实现，后续可扩展为 JWT Token 认证。

---

## 二、HTTP API

### 2.1 消息相关接口

#### 2.1.1 发送消息

**接口描述**：用户发送消息，系统会异步触发 AI 回复。

**请求信息**：
- **URL**: `/api/message/send`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数**：

```json
{
  "content": "你好，我想咨询一个问题",
  "session_id": "user_123"
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | string | 是 | 消息内容，1-5000 字符 |
| session_id | string | 是 | 会话ID（用户ID），1-48 字符 |

**响应示例**：

```json
{
  "id": 1,
  "message_id": "msg_20250127120000_abc12345",
  "session_id": "user_123",
  "from_user_id": "default_user",
  "msg_type": "TEXT",
  "msg_content": "你好，我想咨询一个问题",
  "created_at": "2025-01-27T12:00:00"
}
```

**响应字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 数据库主键ID |
| message_id | string | 消息唯一标识 |
| session_id | string | 会话ID |
| from_user_id | string | 发送人ID |
| msg_type | string | 消息类型：TEXT/AI_REPLY |
| msg_content | string | 消息内容 |
| created_at | datetime | 创建时间 |

**状态码**：

- `200 OK`: 消息发送成功
- `400 Bad Request`: 请求参数错误
- `500 Internal Server Error`: 服务器内部错误

---

#### 2.1.2 获取单条消息

**接口描述**：根据消息ID获取单条消息详情。

**请求信息**：
- **URL**: `/api/message/{message_id}`
- **方法**: `GET`

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| message_id | string | 是 | 消息ID |

**响应示例**：

```json
{
  "id": 1,
  "message_id": "msg_20250127120000_abc12345",
  "session_id": "user_123",
  "from_user_id": "default_user",
  "msg_type": "TEXT",
  "msg_content": "你好，我想咨询一个问题",
  "created_at": "2025-01-27T12:00:00"
}
```

**状态码**：

- `200 OK`: 获取成功
- `404 Not Found`: 消息不存在
- `500 Internal Server Error`: 服务器内部错误

---

#### 2.1.3 获取消息列表

**接口描述**：根据会话ID获取消息列表，支持分页。

**请求信息**：
- **URL**: `/api/message/list`
- **方法**: `GET`

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| session_id | string | 是 | - | 会话ID |
| page | integer | 否 | 1 | 页码，从1开始 |
| page_size | integer | 否 | 20 | 每页数量，最大100 |

**请求示例**：

```
GET /api/message/list?session_id=user_123&page=1&page_size=20
```

**响应示例**：

```json
{
  "messages": [
    {
      "id": 1,
      "message_id": "msg_20250127120000_abc12345",
      "session_id": "user_123",
      "from_user_id": "default_user",
      "msg_type": "TEXT",
      "msg_content": "你好，我想咨询一个问题",
      "created_at": "2025-01-27T12:00:00"
    },
    {
      "id": 2,
      "message_id": "msg_20250127120001_def67890",
      "session_id": "user_123",
      "from_user_id": "ai_bot",
      "msg_type": "AI_REPLY",
      "msg_content": "你好！很高兴为你服务，请告诉我你的问题。",
      "created_at": "2025-01-27T12:00:05"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20
}
```

**响应字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| messages | array | 消息列表 |
| total | integer | 总消息数 |
| page | integer | 当前页码 |
| page_size | integer | 每页数量 |

**状态码**：

- `200 OK`: 获取成功
- `400 Bad Request`: 请求参数错误
- `500 Internal Server Error`: 服务器内部错误

---

### 2.2 AI 相关接口

#### 2.2.1 获取 AI 聊天记录

**接口描述**：获取指定会话的 AI 聊天记录。

**请求信息**：
- **URL**: `/api/ai/records`
- **方法**: `GET`

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| session_id | string | 是 | - | 会话ID |
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量 |

**请求示例**：

```
GET /api/ai/records?session_id=user_123&page=1&page_size=20
```

**响应示例**：

```json
{
  "records": [
    {
      "id": 1,
      "record_id": "record_20250127120000_xyz12345",
      "session_id": "user_123",
      "user_message_id": "msg_20250127120000_abc12345",
      "ai_message_id": "msg_20250127120001_def67890",
      "status": 1,
      "duration_ms": 2500,
      "error_message": null,
      "created_at": "2025-01-27T12:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

**响应字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| records | array | AI 聊天记录列表 |
| total | integer | 总记录数 |
| page | integer | 当前页码 |
| page_size | integer | 每页数量 |

**状态码说明**：

- `0`: 处理中
- `1`: 成功
- `2`: 失败

**状态码**：

- `200 OK`: 获取成功
- `400 Bad Request`: 请求参数错误
- `500 Internal Server Error`: 服务器内部错误

---

### 2.3 健康检查接口

#### 2.3.1 健康检查

**接口描述**：检查服务健康状态。

**请求信息**：
- **URL**: `/health`
- **方法**: `GET`

**响应示例**：

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

**状态码**：

- `200 OK`: 服务正常

---

## 三、WebSocket API

### 3.1 WebSocket 连接

**连接地址**：

```
ws://localhost:8000/ws/{user_id}
```

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | 是 | 用户ID |

**连接示例**：

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user_123');
```

---

### 3.2 消息格式

#### 3.2.1 客户端发送消息

**消息类型**：`send_message`

**消息格式**：

```json
{
  "type": "send_message",
  "content": "你好，我想咨询一个问题"
}
```

**字段说明**：

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| type | string | 是 | 消息类型：send_message |
| content | string | 是 | 消息内容 |

---

#### 3.2.2 服务端推送消息

**消息类型**：`message_sent`

**消息格式**：

```json
{
  "type": "message_sent",
  "message_id": "msg_20250127120000_abc12345",
  "content": "你好，我想咨询一个问题"
}
```

**字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| type | string | 消息类型：message_sent |
| message_id | string | 消息ID |
| content | string | 消息内容 |

---

**消息类型**：`ai_reply`

**消息格式**：

```json
{
  "type": "ai_reply",
  "message_id": "msg_20250127120001_def67890",
  "content": "你好！很高兴为你服务，请告诉我你的问题。",
  "user_message_id": "msg_20250127120000_abc12345"
}
```

**字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| type | string | 消息类型：ai_reply |
| message_id | string | AI 回复消息ID |
| content | string | AI 回复内容 |
| user_message_id | string | 对应的用户消息ID |

---

### 3.3 WebSocket 事件

#### 3.3.1 连接建立

当 WebSocket 连接成功建立时，客户端会收到连接确认。

#### 3.3.2 连接断开

当连接断开时，客户端需要重新连接。

#### 3.3.3 错误处理

如果发生错误，服务端会发送错误消息：

```json
{
  "type": "error",
  "message": "错误信息"
}
```

---

## 四、错误码说明

### 4.1 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 4.2 业务错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 消息内容不能为空 |
| 1002 | 消息内容过长 |
| 1003 | 会话ID不能为空 |
| 2001 | AI 服务调用失败 |
| 2002 | AI 回复超时 |

---

## 五、请求示例

### 5.1 Python 示例

```python
import requests
import json

# 发送消息
url = "http://localhost:8000/api/message/send"
data = {
    "content": "你好，我想咨询一个问题",
    "session_id": "user_123"
}
response = requests.post(url, json=data)
print(response.json())

# 获取消息列表
url = "http://localhost:8000/api/message/list"
params = {
    "session_id": "user_123",
    "page": 1,
    "page_size": 20
}
response = requests.get(url, params=params)
print(response.json())
```

### 5.2 JavaScript 示例

```javascript
// HTTP API
fetch('http://localhost:8000/api/message/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: '你好，我想咨询一个问题',
    session_id: 'user_123'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/user_123');

ws.onopen = () => {
  console.log('WebSocket connected');
  // 发送消息
  ws.send(JSON.stringify({
    type: 'send_message',
    content: '你好，我想咨询一个问题'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
  
  if (message.type === 'ai_reply') {
    console.log('AI回复:', message.content);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```

### 5.3 cURL 示例

```bash
# 发送消息
curl -X POST http://localhost:8000/api/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "content": "你好，我想咨询一个问题",
    "session_id": "user_123"
  }'

# 获取消息列表
curl "http://localhost:8000/api/message/list?session_id=user_123&page=1&page_size=20"

# 获取单条消息
curl "http://localhost:8000/api/message/msg_20250127120000_abc12345"
```

---

## 六、接口调用流程

### 6.1 完整流程示例

```
1. 用户通过 HTTP API 发送消息
   POST /api/message/send
   ↓
2. 服务端保存消息并返回
   响应：message_id
   ↓
3. 服务端异步触发 AI 回复
   Celery 任务处理
   ↓
4. AI 服务生成回复
   LangChain 调用 AI API
   ↓
5. 服务端保存 AI 回复
   数据库保存
   ↓
6. 服务端通过 WebSocket 推送回复
   WebSocket: ai_reply 消息
   ↓
7. 客户端接收 AI 回复
   显示给用户
```

### 6.2 WebSocket 实时通信流程

```
1. 客户端建立 WebSocket 连接
   ws://localhost:8000/ws/user_123
   ↓
2. 客户端发送消息
   {type: "send_message", content: "..."}
   ↓
3. 服务端处理消息
   保存到数据库，触发 AI 回复
   ↓
4. 服务端发送确认
   {type: "message_sent", message_id: "...", content: "..."}
   ↓
5. AI 回复完成后推送
   {type: "ai_reply", message_id: "...", content: "..."}
   ↓
6. 客户端接收并显示
   更新 UI
```

---

## 七、注意事项

### 7.1 请求限制

- 消息内容长度：1-5000 字符
- 分页大小：最大 100
- WebSocket 连接数：建议不超过 1000

### 7.2 超时设置

- HTTP 请求超时：30 秒
- WebSocket 连接超时：无限制（建议客户端实现心跳）
- AI 回复超时：300 秒（5 分钟）

### 7.3 错误处理

- 所有错误都会返回 JSON 格式的错误信息
- 客户端应该根据错误码进行相应的处理
- 建议实现重试机制

---

**文档版本**：v1.0  
**创建时间**：2025-01-27  
**最后更新**：2025-01-27

