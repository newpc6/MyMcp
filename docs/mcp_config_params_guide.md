# MCP 配置参数替换格式指南

本文档介绍了AI-MCP中如何使用配置参数替换功能，使开发者可以轻松创建带有动态配置的模块。

## 配置参数替换标准格式

AI-MCP使用 `${参数名}` 作为统一的标准替换格式。系统在启动服务时会自动将这些占位符替换为实际的配置值。

### 使用方法

1. 在代码中使用 `${参数名}` 格式定义需要替换的参数
2. 在模块配置中定义对应的参数
3. 发布服务时填写参数值

### 示例

```python
# 数据库连接示例
def connect_database():
    """
    连接到数据库

    平台配置参数 (使用${参数名}格式):
    ${database_host}: 数据库主机地址
    ${database_port}: 数据库端口
    ${database_user}: 数据库用户名
    ${database_password}: 数据库密码
    ${database_name}: 数据库名称
    """
    connection = pymysql.connect(
        host="${database_host}",
        port=int("${database_port}"),
        user="${database_user}",
        password="${database_password}",
        database="${database_name}",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
```

### 数据类型处理

* 字符串类型: 系统会自动添加引号，如 `"${api_key}"` 替换为 `"your_actual_key"`
* 数字类型: 系统不会添加引号，如 `${port}` 替换为 `3306`
* 布尔类型: 系统不会添加引号，如 `${enable_feature}` 替换为 `True`

### 文档注释规范

为了使其他开发者能够理解您的模块需要哪些配置参数，建议在函数文档字符串中使用以下格式：

```python
"""
函数描述

工具参数:
param1 (type): 描述

平台配置参数 (使用${参数名}格式):
${param1}: 参数1的描述
${param2}: 参数2的描述

返回:
返回值描述
"""
```

## 向后兼容性

为了保持向后兼容性，系统仍然支持以下格式的参数替换：

```python
param_name = "REPLACE_ME"  # 旧格式，仍然支持
```

但对于新开发的模块，我们建议使用 `${param_name}` 标准格式。

## 常见问题

### 1. 参数替换失败

如果参数替换失败，请检查：

- 参数名称是否正确
- 参数名称在模块配置中是否定义
- 替换格式是否正确 (`${参数名}`)

### 2. 如何处理数字类型参数

对于数字类型参数，您可以使用 `int()` 或 `float()` 转换，例如：

```python
port=int("${database_port}")
```

系统将先替换字符串，然后由Python执行转换。
