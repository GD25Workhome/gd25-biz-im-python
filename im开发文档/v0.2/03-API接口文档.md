# IM 服务 - API 接口文档（v0.2）

## 一、API 概述

### 1.1 基础信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: v1
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2 认证方式

当前版本简化实现，后续可扩展为 JWT Token 认证。

### 1.3 错误响应格式

所有错误响应统一使用以下格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息",
    "details": {}
  }
}
```

---

## 二、IM核心 API

### 2.1 用户相关接口

#### 2.1.1 创建用户

**接口描述**：创建新用户。

**请求信息**：
- **URL**: `/api/user/create`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数**：

```json
{
  "username": "张三",
  "user_role": "PATIENT"
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| username | string | 是 | 用户名 | 1-64字符 |
| user_role | string | 是 | 用户身份 | 可选值：'PATIENT'/'DOCTOR'/'AI_ASSISTANT' |

**响应示例**：

```json
{
  "id": 1,
  "user_id": "user_20250127120000_abc12345",
  "username": "张三",
  "user_role": "PATIENT",
  "created_at": "2025-01-27T12:00:00",
  "updated_at": "2025-01-27T12:00:00"
}
```

**响应字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 数据库主键ID |
| user_id | string | 用户唯一标识 |
| username | string | 用户名 |
| user_role | string | 用户身份 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

**状态码**：

- `200 OK`: 用户创建成功
- `400 Bad Request`: 请求参数错误（如user_role无效）
- `500 Internal Server Error`: 服务器内部错误

---

#### 2.1.2 获取用户信息

**接口描述**：根据用户ID获取用户信息。

**请求信息**：
- **URL**: `/api/user/{user_id}`
- **方法**: `GET`

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | 是 | 用户ID |

**响应示例**：

```json
{
  "id": 1,
  "user_id": "user_20250127120000_abc12345",
  "username": "张三",
  "user_role": "PATIENT",
  "created_at": "2025-01-27T12:00:00",
  "updated_at": "2025-01-27T12:00:00"
}
```

**状态码**：

- `200 OK`: 获取成功
- `404 Not Found`: 用户不存在
- `500 Internal Server Error`: 服务器内部错误

---

#### 2.1.3 更新用户身份标签

**接口描述**：更新用户的身份标签。

**请求信息**：
- **URL**: `/api/user/{user_id}/role`
- **方法**: `PUT`
- **Content-Type**: `application/json`

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | 是 | 用户ID |

**请求参数**：

```json
{
  "user_role": "DOCTOR"
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| user_role | string | 是 | 新的用户身份 | 可选值：'PATIENT'/'DOCTOR'/'AI_ASSISTANT' |

**响应示例**：

```json
{
  "id": 1,
  "user_id": "user_20250127120000_abc12345",
  "username": "张三",
  "user_role": "DOCTOR",
  "created_at": "2025-01-27T12:00:00",
  "updated_at": "2025-01-27T12:05:00"
}
```

**状态码**：

- `200 OK`: 更新成功
- `400 Bad Request`: 请求参数错误（如user_role无效）
- `404 Not Found`: 用户不存在
- `500 Internal Server Error`: 服务器内部错误

---

### 2.2 群组相关接口

#### 2.2.1 创建群组

**接口描述**：创建新群组。

**请求信息**：
- **URL**: `/api/group/create`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数**：

```json
{
  "group_name": "医疗咨询群",
  "description": "患者与医生的咨询群组"
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| group_name | string | 是 | 群组名称 | 1-128字符 |
| description | string | 否 | 群组描述 | 可为空 |

**响应示例**：

```json
{
  "id": 1,
  "group_id": "group_20250127120000_xyz12345",
  "group_name": "医疗咨询群",
  "description": "患者与医生的咨询群组",
  "created_by": "user_20250127120000_abc12345",
  "created_at": "2025-01-27T12:00:00",
  "updated_at": "2025-01-27T12:00:00"
}
```

**响应字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 数据库主键ID |
| group_id | string | 群组唯一标识 |
| group_name | string | 群组名称 |
| description | string | 群组描述 |
| created_by | string | 创建人ID |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

**状态码**：

- `200 OK`: 群组创建成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 创建人不存在
- `500 Internal Server Error`: 服务器内部错误

**说明**：
- 创建群组时，创建人会自动添加为群组成员，身份标签默认为'DOCTOR'

---

#### 2.2.2 获取群组信息

**接口描述**：根据群组ID获取群组信息。

**请求信息**：
- **URL**: `/api/group/{group_id}`
- **方法**: `GET`

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| group_id | string | 是 | 群组ID |

**响应示例**：

```json
{
  "id": 1,
  "group_id": "group_20250127120000_xyz12345",
  "group_name": "医疗咨询群",
  "description": "患者与医生的咨询群组",
  "created_by": "user_20250127120000_abc12345",
  "created_at": "2025-01-27T12:00:00",
  "updated_at": "2025-01-27T12:00:00"
}
```

**状态码**：

- `200 OK`: 获取成功
- `404 Not Found`: 群组不存在
- `500 Internal Server Error`: 服务器内部错误

---

#### 2.2.3 添加群组成员

**接口描述**：向群组添加成员。

**请求信息**：
- **URL**: `/api/group/{group_id}/members`
- **方法**: `POST`
- **Content-Type**: `application/json`

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| group_id | string | 是 | 群组ID |

**请求参数**：

```json
{
  "user_id": "user_20250127120001_def67890",
  "user_role": "PATIENT"
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| user_id | string | 是 | 用户ID | 1-48字符 |
| user_role | string | 是 | 用户在群组中的身份标签 | 可选值：'PATIENT'/'DOCTOR'/'AI_ASSISTANT' |

**响应示例**：

```json
{
  "success": true,
  "message": "Member added successfully"
}
```

**状态码**：

- `200 OK`: 成员添加成功
- `400 Bad Request`: 请求参数错误（如用户已在群组中）
- `404 Not Found`: 群组不存在或用户不存在
- `500 Internal Server Error`: 服务器内部错误

**说明**：
- `user_role` 表示**用户在群组中的身份标签**，可能与用户在系统中的全局身份不同
- 如果用户已在群组中，返回400错误

---

#### 2.2.4 获取群组成员列表

**接口描述**：获取群组的所有成员列表。

**请求信息**：
- **URL**: `/api/group/{group_id}/members`
- **方法**: `GET`

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| group_id | string | 是 | 群组ID |

**响应示例**：

```json
{
  "group_id": "group_20250127120000_xyz12345",
  "members": [
    {
      "user_id": "user_20250127120000_abc12345",
      "user_role": "DOCTOR",
      "joined_at": "2025-01-27T12:00:00"
    },
    {
      "user_id": "user_20250127120001_def67890",
      "user_role": "PATIENT",
      "joined_at": "2025-01-27T12:01:00"
    }
  ],
  "total": 2
}
```

**响应字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| group_id | string | 群组ID |
| members | array | 成员列表 |
| members[].user_id | string | 用户ID |
| members[].user_role | string | 用户在群组中的身份标签 |
| members[].joined_at | datetime | 加入时间 |
| total | integer | 成员总数 |

**状态码**：

- `200 OK`: 获取成功
- `404 Not Found`: 群组不存在
- `500 Internal Server Error`: 服务器内部错误

---

### 2.3 消息相关接口

#### 2.3.1 发送消息

**接口描述**：在群组中发送消息。如果发送人是患者，消息会自动转发给AI服务。

**请求信息**：
- **URL**: `/api/message/send`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数**：

```json
{
  "group_id": "group_20250127120000_xyz12345",
  "content": "你好，我想咨询一个问题"
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| group_id | string | 是 | 群组ID | 1-64字符 |
| content | string | 是 | 消息内容 | 1-5000字符 |

**响应示例**：

```json
{
  "id": 1,
  "message_id": "msg_20250127120000_abc12345",
  "group_id": "group_20250127120000_xyz12345",
  "from_user_id": "user_20250127120001_def67890",
  "msg_type": "TEXT",
  "msg_content": "你好，我想咨询一个问题",
  "created_at": "2025-01-27T12:00:00",
  "updated_at": "2025-01-27T12:00:00"
}
```

**响应字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 数据库主键ID |
| message_id | string | 消息唯一标识 |
| group_id | string | 群组ID |
| from_user_id | string | 发送人ID |
| msg_type | string | 消息类型：TEXT/IMAGE/AI_REPLY |
| msg_content | string | 消息内容 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

**状态码**：

- `200 OK`: 消息发送成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 群组不存在或发送人不在群组中
- `500 Internal Server Error`: 服务器内部错误

**说明**：
- 如果发送人是患者（`group_members.user_role = 'PATIENT'`），消息会自动转发给AI服务
- AI回复会通过WebSocket推送，不会在HTTP响应中返回
- 如果发送人是医生（`group_members.user_role = 'DOCTOR'`），消息不会转发给AI服务

---

#### 2.3.2 获取消息列表

**接口描述**：获取群组的消息列表，支持分页。

**请求信息**：
- **URL**: `/api/message/list`
- **方法**: `GET`

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 约束 |
|--------|------|------|--------|------|------|
| group_id | string | 是 | - | 群组ID | 1-64字符 |
| page | integer | 否 | 1 | 页码 | >= 1 |
| page_size | integer | 否 | 20 | 每页数量 | 1-100 |

**请求示例**：

```
GET /api/message/list?group_id=group_20250127120000_xyz12345&page=1&page_size=20
```

**响应示例**：

```json
{
  "messages": [
    {
      "id": 1,
      "message_id": "msg_20250127120000_abc12345",
      "group_id": "group_20250127120000_xyz12345",
      "from_user_id": "user_20250127120001_def67890",
      "msg_type": "TEXT",
      "msg_content": "你好，我想咨询一个问题",
      "created_at": "2025-01-27T12:00:00",
      "updated_at": "2025-01-27T12:00:00"
    },
    {
      "id": 2,
      "message_id": "msg_20250127120001_xyz67890",
      "group_id": "group_20250127120000_xyz12345",
      "from_user_id": "ai_assistant_001",
      "msg_type": "AI_REPLY",
      "msg_content": "你好！很高兴为你服务，请告诉我你的问题。",
      "created_at": "2025-01-27T12:00:05",
      "updated_at": "2025-01-27T12:00:05"
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
| messages | array | 消息列表（按创建时间倒序） |
| total | integer | 总消息数 |
| page | integer | 当前页码 |
| page_size | integer | 每页数量 |

**状态码**：

- `200 OK`: 获取成功
- `400 Bad Request`: 请求参数错误（如分页参数无效）
- `404 Not Found`: 群组不存在
- `500 Internal Server Error`: 服务器内部错误

---

#### 2.3.3 获取单条消息

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
  "group_id": "group_20250127120000_xyz12345",
  "from_user_id": "user_20250127120001_def67890",
  "msg_type": "TEXT",
  "msg_content": "你好，我想咨询一个问题",
  "created_at": "2025-01-27T12:00:00",
  "updated_at": "2025-01-27T12:00:00"
}
```

**状态码**：

- `200 OK`: 获取成功
- `404 Not Found`: 消息不存在
- `500 Internal Server Error`: 服务器内部错误

---

## 三、AI封装层 API（可选）

### 3.1 AI交互记录接口

#### 3.1.1 获取AI交互记录

**接口描述**：获取群组的AI交互记录列表。

**请求信息**：
- **URL**: `/api/ai/interactions`
- **方法**: `GET`

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 约束 |
|--------|------|------|--------|------|------|
| group_id | string | 是 | - | 群组ID | 1-64字符 |
| page | integer | 否 | 1 | 页码 | >= 1 |
| page_size | integer | 否 | 20 | 每页数量 | 1-100 |

**请求示例**：

```
GET /api/ai/interactions?group_id=group_20250127120000_xyz12345&page=1&page_size=20
```

**响应示例**：

```json
{
  "records": [
    {
      "id": 1,
      "record_id": "record_20250127120000_xyz12345",
      "group_id": "group_20250127120000_xyz12345",
      "user_message_id": "msg_20250127120000_abc12345",
      "ai_message_id": "msg_20250127120001_xyz67890",
      "ai_service_url": "https://ai-service.example.com/api/chat",
      "status": 1,
      "duration_ms": 2500,
      "error_message": null,
      "created_at": "2025-01-27T12:00:00",
      "updated_at": "2025-01-27T12:00:05"
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
| records | array | AI交互记录列表 |
| records[].status | integer | 状态：0-处理中，1-成功，2-失败 |
| total | integer | 总记录数 |
| page | integer | 当前页码 |
| page_size | integer | 每页数量 |

**状态码**：

- `200 OK`: 获取成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 群组不存在
- `500 Internal Server Error`: 服务器内部错误

---

## 四、WebSocket API

### 4.1 WebSocket 连接

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
const ws = new WebSocket('ws://localhost:8000/ws/user_20250127120000_abc12345');
```

---

### 4.2 消息格式

#### 4.2.1 客户端发送消息

**消息类型**：`send_message`

**消息格式**：

```json
{
  "type": "send_message",
  "group_id": "group_20250127120000_xyz12345",
  "content": "你好，我想咨询一个问题"
}
```

**字段说明**：

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| type | string | 是 | 消息类型：send_message |
| group_id | string | 是 | 群组ID |
| content | string | 是 | 消息内容 |

---

#### 4.2.2 服务端推送消息

**消息类型**：`message_sent`

**消息格式**：

```json
{
  "type": "message_sent",
  "message_id": "msg_20250127120000_abc12345",
  "group_id": "group_20250127120000_xyz12345",
  "from_user_id": "user_20250127120001_def67890",
  "content": "你好，我想咨询一个问题",
  "created_at": "2025-01-27T12:00:00"
}
```

**字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| type | string | 消息类型：message_sent |
| message_id | string | 消息ID |
| group_id | string | 群组ID |
| from_user_id | string | 发送人ID |
| content | string | 消息内容 |
| created_at | datetime | 创建时间 |

---

**消息类型**：`ai_reply`

**消息格式**：

```json
{
  "type": "ai_reply",
  "message_id": "msg_20250127120001_xyz67890",
  "group_id": "group_20250127120000_xyz12345",
  "from_user_id": "ai_assistant_001",
  "content": "你好！很高兴为你服务，请告诉我你的问题。",
  "user_message_id": "msg_20250127120000_abc12345",
  "created_at": "2025-01-27T12:00:05"
}
```

**字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| type | string | 消息类型：ai_reply |
| message_id | string | AI回复消息ID |
| group_id | string | 群组ID |
| from_user_id | string | 发送人ID（AI助手ID） |
| content | string | AI回复内容 |
| user_message_id | string | 对应的用户消息ID |
| created_at | datetime | 创建时间 |

---

### 4.3 WebSocket 事件

#### 4.3.1 连接建立

当 WebSocket 连接成功建立时，客户端会收到连接确认。

#### 4.3.2 连接断开

当连接断开时，客户端需要重新连接。

#### 4.3.3 错误处理

如果发生错误，服务端会发送错误消息：

```json
{
  "type": "error",
  "code": "ERROR_CODE",
  "message": "错误信息"
}
```

---

## 五、错误码说明

### 5.1 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 5.2 业务错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 消息内容不能为空 |
| 1002 | 消息内容过长（超过5000字符） |
| 1003 | 群组ID不能为空 |
| 2001 | 用户不存在 |
| 2002 | 用户已在群组中 |
| 2003 | 用户不在群组中 |
| 3001 | 群组不存在 |
| 4001 | AI服务调用失败 |
| 4002 | AI服务超时 |
| 4003 | AI服务返回格式错误 |

---

## 六、请求示例

### 6.1 Python 示例

```python
import requests
import json

# 创建用户
url = "http://localhost:8000/api/user/create"
data = {
    "username": "张三",
    "user_role": "PATIENT"
}
response = requests.post(url, json=data)
print(response.json())

# 创建群组
url = "http://localhost:8000/api/group/create"
data = {
    "group_name": "医疗咨询群",
    "description": "患者与医生的咨询群组"
}
response = requests.post(url, json=data)
group_data = response.json()
group_id = group_data["group_id"]

# 发送消息
url = "http://localhost:8000/api/message/send"
data = {
    "group_id": group_id,
    "content": "你好，我想咨询一个问题"
}
response = requests.post(url, json=data)
print(response.json())
```

### 6.2 JavaScript 示例

```javascript
// HTTP API
fetch('http://localhost:8000/api/message/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    group_id: 'group_20250127120000_xyz12345',
    content: '你好，我想咨询一个问题'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/user_20250127120000_abc12345');

ws.onopen = () => {
  console.log('WebSocket connected');
  // 发送消息
  ws.send(JSON.stringify({
    type: 'send_message',
    group_id: 'group_20250127120000_xyz12345',
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
```

---

## 七、接口调用流程

### 7.1 完整流程示例（患者发送消息）

```
1. 患者通过 HTTP API 发送消息
   POST /api/message/send
   {
     "group_id": "group_xxx",
     "content": "你好"
   }
   ↓
2. 服务端保存消息并返回
   响应：message_id
   ↓
3. AI封装层识别用户身份（患者）
   ↓
4. AI封装层判断需要转发给AI服务
   ↓
5. AI封装层异步调用外部AI服务（HTTP API）
   ↓
6. AI服务返回回复
   ↓
7. AI封装层创建AI助手消息
   ↓
8. 服务端保存AI回复消息
   ↓
9. 服务端通过WebSocket推送AI回复给群组所有成员
   WebSocket: {
     "type": "ai_reply",
     "message_id": "...",
     "content": "..."
   }
```

### 7.2 完整流程示例（医生发送消息）

```
1. 医生通过 HTTP API 发送消息
   POST /api/message/send
   {
     "group_id": "group_xxx",
     "content": "你好"
   }
   ↓
2. 服务端保存消息并返回
   响应：message_id
   ↓
3. AI封装层识别用户身份（医生）
   ↓
4. AI封装层判断不需要转发给AI服务
   ↓
5. 服务端通过WebSocket推送消息给群组所有成员
   WebSocket: {
     "type": "message_sent",
     "message_id": "...",
     "content": "..."
   }
```

---

## 八、注意事项

### 8.1 请求限制

- 消息内容长度：1-5000 字符
- 分页大小：最大 100
- WebSocket 连接数：建议不超过 1000

### 8.2 超时设置

- HTTP 请求超时：30 秒
- WebSocket 连接超时：无限制（建议客户端实现心跳）
- AI 服务调用超时：30 秒（可配置）

### 8.3 错误处理

- 所有错误都会返回 JSON 格式的错误信息
- 客户端应该根据错误码进行相应的处理
- 建议实现重试机制

### 8.4 用户身份说明

- **用户系统身份**（`users.user_role`）：用户在系统中的全局身份
- **群组身份标签**（`group_members.user_role`）：用户在特定群组中的身份
- **消息路由规则**：基于**群组身份标签**判断是否转发给AI，而不是系统身份

---

**文档版本**：v0.2  
**创建时间**：2025-01-27  
**最后更新**：2025-01-27  
**更新说明**：重新设计，实现IM核心与AI服务的完全解耦
