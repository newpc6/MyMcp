# MCP 鉴权模型模块 (models/auth)

## 职责边界

定义已发布 MCP 服务的鉴权相关数据模型：密钥、密钥统计和访问日志。模型层只保留 ORM 字段和必要序列化，不自行打开数据库连接。

## 目录/文件说明

- `published_service_secret.py`：`McpServiceSecret` 密钥表模型。
- `published_service_secret_statistics.py`：`McpSecretStatistics` 密钥按日统计模型。
- `published_service_access_log.py`：`McpAccessLog` 访问日志模型。
- `__init__.py`：统一导出以上三个模型。

## 实体/表说明

### McpServiceSecret (published_service_secrets)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 密钥 ID |
| service_id | Integer FK | 关联发布服务 |
| secret_key | String(255) UNIQUE | 密钥字符串 |
| secret_name | String(100) | 密钥名称 |
| description | Text | 描述 |
| is_active | Boolean | 是否激活 |
| limit_count | Integer | 日调用限制（0=无限制） |
| created_at / updated_at | DateTime | 时间戳 |
| expires_at | DateTime | 过期时间（NULL=永不过期） |
| user_id | Integer FK | 创建者用户 ID |

### McpSecretStatistics (published_service_secret_statistics)

每密钥每天一条统计记录，联合唯一约束 `(secret_id, statistics_date)`。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| secret_id | Integer FK | 关联密钥 |
| service_id | Integer FK | 关联服务 |
| call_count | Integer | 当日调用次数 |
| success_count | Integer | 成功次数 |
| error_count | Integer | 错误次数 |
| last_access_at | DateTime | 最后访问时间 |
| statistics_date | Date | 统计日期 |

### McpAccessLog (published_service_access_logs)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| service_id | Integer FK | 关联服务 |
| secret_id | Integer FK | 关联密钥（可空） |
| client_ip | String(45) | 客户端 IP |
| user_agent | Text | User-Agent |
| access_time | DateTime | 访问时间 |
| status | String(20) | success / error / forbidden |
| error_message | Text | 错误详情 |
| request_headers | Text | JSON 格式请求头 |

## 兼容性风险

- 2026-06-30：`McpServiceSecret.get_creator_name()` 不再自行调用 `get_db()`，始终返回 None。调用方需通过 `McpAuthRepository.get_creator_name()` 查询后传入 `to_dict(creator_name=...)`。
- `McpServiceSecret.to_dict()` 新增可选参数 `creator_name`，向后兼容：不传时回退到 `get_creator_name()`（返回 None）。

## 验证方式

```powershell
cd backend
conda run -n mcp python -m py_compile app/models/auth/published_service_secret.py
conda run -n mcp python -c "from app.models.auth import McpServiceSecret; print('OK')"
```

## 改动记录

- 2026-06-30：`McpServiceSecret.get_creator_name()` 移除 `get_db()` 副作用，返回 None；`to_dict()` 新增可选 `creator_name` 参数。
