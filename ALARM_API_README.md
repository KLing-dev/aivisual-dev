# 警报API接口文档

## 1. 接口概述

本API提供了基于RabbitMQ的警报信息发送功能，用于将告警信息可靠地发送至消息队列。该接口严格遵循指定的参数格式和数据类型要求，确保告警信息的完整性和可靠性。

## 2. 接口列表

| 接口名称 | 请求方法 | 请求路径 | 功能描述 |
|---------|---------|---------|---------|
| 发送告警 | POST | /send_alarm | 发送单条告警信息到RabbitMQ队列 |
| 批量发送告警 | POST | /batch_send_alarm | 批量发送多条告警信息到RabbitMQ队列 |

## 3. 接口详细说明

### 3.1 发送告警接口

#### 请求路径
```
POST /send_alarm
```

#### 请求参数

| 参数名 | 必填 | 类型 | 说明 |
|-------|------|------|------|
| code | 否 | string | 记录唯一标识，不提供则自动生成 |
| alarmTime | 是 | datetime | 告警时间，格式：yyyy-MM-dd HH:mm:ss |
| deviceCode | 否 | string | 设备唯一标识 |
| deviceName | 否 | string | 设备名称 |
| level | 否 | string | 告警级别 |
| memo | 否 | string | 告警内容 |
| image | 否 | string | 告警照片，url |
| position | 否 | string | 位置 |
| personCode | 否 | string | 人员唯一标识 |
| personName | 否 | string | 人员姓名 |
| ext1 | 否 | string | 扩展字段json |

#### 响应示例

```json
{
  "status": "success",
  "message": "告警信息已成功发送到消息队列",
  "data": {
    "code": "550e8400-e29b-41d4-a716-446655440000",
    "alarmType": 1,
    "subType": "异常行为识别",
    "alarmTime": "2023-10-01 12:00:00",
    "deviceCode": "camera_001",
    "deviceName": "摄像头1",
    "level": "high",
    "memo": "检测到异常行为",
    "image": "http://example.com/alarm.jpg",
    "position": "大厅",
    "personCode": "person_001",
    "personName": "张三",
    "ext1": "{\"additional_info\": \"test\"}"
  }
}
```

### 3.2 批量发送告警接口

#### 请求路径
```
POST /batch_send_alarm
```

#### 请求参数

| 参数名 | 必填 | 类型 | 说明 |
|-------|------|------|------|
| alarms | 是 | array | 告警信息列表，每个告警信息的字段与send_alarm接口相同 |

#### 响应示例

```json
{
  "status": "success",
  "message": "批量发送完成，成功2条，失败0条",
  "data": {
    "total": 2,
    "success_count": 2,
    "failed_count": 0,
    "failed_alarms": []
  }
}
```

## 4. 调用示例

### 4.1 Python调用示例

```python
import requests
import json
from datetime import datetime

# 接口地址
url = "http://localhost:8000/send_alarm"

# 请求数据
payload = {
    "alarmTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "deviceCode": "camera_001",
    "deviceName": "摄像头1",
    "level": "high",
    "memo": "检测到异常行为",
    "image": "http://example.com/alarm.jpg",
    "position": "大厅",
    "personCode": "person_001",
    "personName": "张三",
    "ext1": json.dumps({"additional_info": "test"})
}

# 发送请求
response = requests.post(url, json=payload)

# 打印响应
print(response.status_code)
print(response.json())
```

### 4.2 批量发送示例

```python
import requests
import json
from datetime import datetime

# 接口地址
url = "http://localhost:8000/batch_send_alarm"

# 请求数据
payload = {
    "alarms": [
        {
            "alarmTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "deviceCode": "camera_001",
            "deviceName": "摄像头1",
            "level": "high",
            "memo": "检测到异常行为1"
        },
        {
            "alarmTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "deviceCode": "camera_002",
            "deviceName": "摄像头2",
            "level": "medium",
            "memo": "检测到异常行为2"
        }
    ]
}

# 发送请求
response = requests.post(url, json=payload)

# 打印响应
print(response.status_code)
print(response.json())
```

### 4.3 cURL调用示例

```bash
curl -X POST "http://localhost:8000/send_alarm" \
  -H "Content-Type: application/json" \
  -d '{"alarmTime": "2023-10-01 12:00:00", "deviceCode": "camera_001", "deviceName": "摄像头1", "level": "high", "memo": "检测到异常行为"}'
```

## 5. 消息格式说明

发送到RabbitMQ队列的消息采用JSON格式，包含以下字段：

```json
{
  "code": "550e8400-e29b-41d4-a716-446655440000",
  "alarmType": 1,  // 固定为数值"1"
  "subType": "异常行为识别",  // 固定为"异常行为识别"
  "alarmTime": "2023-10-01 12:00:00",
  "deviceCode": "camera_001",
  "deviceName": "摄像头1",
  "level": "high",
  "memo": "检测到异常行为",
  "image": "http://example.com/alarm.jpg",
  "position": "大厅",
  "personCode": "person_001",
  "personName": "张三",
  "ext1": "{\"additional_info\": \"test\"}"
}
```

## 6. 错误码说明

| 错误码 | 错误信息 | 说明 |
|-------|---------|------|
| 400 | 请求参数错误 | 请求参数格式或类型不正确 |
| 500 | 服务器内部错误 | 服务器处理请求时发生错误 |

## 7. 技术实现细节

### 7.1 RabbitMQ配置

| 配置项 | 值 | 说明 |
|-------|-----|------|
| 主机 | localhost | RabbitMQ服务器地址 |
| 端口 | 5672 | RabbitMQ服务器端口 |
| 用户名 | guest | RabbitMQ用户名 |
| 密码 | guest | RabbitMQ密码 |
| 虚拟主机 | / | RabbitMQ虚拟主机 |
| 交换机 | alarm_exchange | 告警消息交换机 |
| 交换机类型 | direct | 交换机类型 |
| 队列 | alarm_queue | 告警消息队列 |
| 路由键 | alarm_routing_key | 消息路由键 |
| 消息持久化 | True | 消息持久化存储 |

### 7.2 错误处理机制

1. **连接失败重试**：当与RabbitMQ服务器连接失败时，会自动重试连接，最大重试次数为3次，每次重试间隔5秒
2. **消息发送确认**：确保消息成功发送到RabbitMQ队列
3. **异常日志记录**：详细记录连接错误、发送错误等异常信息
4. **连接状态管理**：自动检测连接状态，连接断开时自动重新连接

## 8. 部署和运行

### 8.1 环境要求

- Python 3.7+
- FastAPI 0.68.0+
- uvicorn 0.15.0+
- pika 1.3.2+
- amqpstorm 2.8.6+

### 8.2 启动服务

```bash
# 进入项目根目录
cd /path/to/project

# 启动API服务
uvicorn api.cv_api:app --host 0.0.0.0 --port 8000
```

### 8.3 访问API文档

启动服务后，可以通过以下地址访问自动生成的API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 9. 测试

### 9.1 单元测试

项目包含单元测试，用于验证消息发送功能的正确性和可靠性。运行测试命令：

```bash
# 运行单元测试
python -m pytest tests/test_alarm_api.py -v
```

### 9.2 手动测试

可以使用Postman、curl等工具手动测试API接口，验证告警信息是否能成功发送到RabbitMQ队列。

## 10. 注意事项

1. 告警类型字段`alarmType`固定为数值"1"，表示摄像头告警
2. 告警子类型字段`subType`固定为"异常行为识别"
3. 告警时间字段`alarmTime`必须严格按照"yyyy-MM-dd HH:mm:ss"格式提供
4. 扩展字段`ext1`必须是有效的JSON字符串
5. 建议在生产环境中修改RabbitMQ的默认用户名和密码，提高安全性
6. 建议根据实际需求调整RabbitMQ的连接重试次数和间隔时间
7. 建议在生产环境中配置合适的日志级别和日志存储策略

## 11. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2025-01-01 | 初始版本，实现基本的告警信息发送功能 |
