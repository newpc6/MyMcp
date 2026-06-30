# MCP 鉴权服务模块 (services/auth)

## 职责边界

负责 MCP 服务密钥的生成、验证、激活/禁用、删除、统计和访问日志记录。密钥业务规则和权限判断在此层完成，数据库查询委托给 `McpAuthRepository`。

## 目录/文件说明

- `secret_manager.py`：`SecretManager` 密钥管理器，是鉴权服务唯一的公开入口。
- `__init__.py`：导出 `SecretManager`。

## 核心流程

1. **密钥生成** (`generate_secret`)：校验服务存在 → 检查密钥数上限 → 生成密钥字符串 → 创建记录 → commit → 返回带完整密钥的字典。
2. **密钥验证** (`validate_secret`)：查密钥记录 → 检查过期 → 检查调用次数限制 (limit_count) → 返回验证结果。
3. **访问记录** (`log_access`)：写入 `McpAccessLog` 记录 → 若有关联密钥则调用 `update_secret_statistics` 更新当日统计。
4. **统计获取** (`get_secret_statistics` / `get_secret_info`)：从 Repository 获取统计数据，聚合计算总调用次数、成功率等。

## 依赖关系

- `McpAuthRepository`：所有数据库查询和持久化辅助。
- `SecretGenerator`：密钥字符串生成和过期计算。
- `McpService` / `McpServiceSecret` / `McpSecretStatistics` / `McpAccessLog` 模型：ORM 实体。
- `mcp_logger`：日志输出。
- `error_code`：业务错误码。

## 配置项

- 单服务最大密钥数：硬编码 50（`generate_secret` 中 `max_secrets`）。
- 统计默认天数：30 天（`get_secret_statistics` 默认 `days=30`）。

## 常见改动点

- 调整密钥数上限：修改 `generate_secret` 中的 `max_secrets`。
- 新增密钥属性：在 `update_secret` 中增加字段更新逻辑。
- 新增统计维度：在 `get_secret_info` 中扩展聚合计算。

## 验证方式

```powershell
cd backend
conda run -n mcp python -m py_compile app/services/auth/secret_manager.py
conda run -n mcp python -c "from app.services.auth import SecretManager; print('OK')"
```

## 改动记录

- 2026-06-30：引入 `McpAuthRepository`，将所有数据库查询从 SecretManager 迁移到 Repository；新增 `_to_dict_with_creator` / `_to_dict_list_with_creators` 辅助方法，批量获取 creator_name 后传入 `McpServiceSecret.to_dict()`。
