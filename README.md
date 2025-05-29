# MyMcp

## 介绍

开源介绍 https://blog.csdn.net/u012327423/article/details/147531100

## 软件架构

软件架构说明

## 模块说明

### 登录页面

![login-v2.jpg](https://img.picui.cn/free/2025/05/29/683830b4d8b57.jpg)
### MCP模板广场

![mcp-squera-v2.jpg](https://img.picui.cn/free/2025/05/29/6838001fac033.jpg)


#### MCP模板 详情

![detail-v2.jpg](https://img.picui.cn/free/2025/05/29/683857a0d89fd.jpg)

#### MCP 工具-测试

[![tool1.jpg](https://img.picui.cn/free/2025/05/13/68234a4668f1d.jpg)](https://img.picui.cn/free/2025/05/13/68234a4668f1d.jpg)

#### MCP 服务发布-参数配置

[![tool2.jpg](https://img.picui.cn/free/2025/05/13/68234a466f775.jpg)](https://img.picui.cn/free/2025/05/13/68234a466f775.jpg)

### MCP 服务

![mcp-service-v2.jpg](https://img.picui.cn/free/2025/05/29/68381d521f1c5.jpg)

### MCP 统计

![mcp-stat-v2.jpg](https://img.picui.cn/free/2025/05/29/68384779bc6c9.jpg)

### 用户管理

![user-v2.jpg](https://img.picui.cn/free/2025/05/29/68385ad42653d.jpg)

## 临时体验地址

http://111.4.141.154:7002

guest/123456

admin/eGova@2025(管理员账号请勿随意删除修改数据，主要是为了看功能)

## 安装教程

### 1. 拉取项目

拉取工程到本地

### 2. 后端

## 2.1 创建 python 环境

以 conda 为例，创建 conda 环境，命名可以是 mcp。python 版本推荐 3.11

等待创建成功后

切换为刚创建的 conda 环境

```
conda activate mcp-test
```

进入后端目录，安装 python 依赖，推荐清华源

```
cd backend
pip install -r .\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 2.2 调整配置文件

新建配置文件，在 backend 路径下，复制 config.jsonbak 为 config.json

## 2.3 配置文件结构

配置文件`backend/config.json`包含以下主要部分：

### 1. cors（跨域资源共享配置）

```json
"cors": {
    "origins": ["*"],           // 允许的来源域，"*"表示允许所有域
    "credentials": true,        // 是否允许发送身份凭证
    "methods": ["*"],           // 允许的HTTP方法，"*"表示允许所有方法
    "headers": ["*"]            // 允许的HTTP头，"*"表示允许所有头信息
}
```

### 2. api（API 配置）

```json
"api": {
    "prefix": "/api",           // API路径前缀
    "title": "MCP Server", // API标题
    "version": "1.0.0"          // API版本号
}
```

### 3. server（服务器配置）

```json
"server": {
    "host": "0.0.0.0",          // 服务器绑定地址，0.0.0.0表示监听所有网络接口
    "port": 8002,               // 服务器监听端口
    "debug": true               // 是否开启调试模式
}
```

### 4. mcp（废弃）

### 5. logging（日志配置）

```json
"logging": {
    "level": "info",            // 日志级别
    "backup_count": 7           // 日志备份数量
}
```

### 6. database（数据库配置）

```json
"database": {
    "type": "mysql",            // 数据库类型，支持mysql和sqlite
    "file": "mcp.db",     // 数据库文件（用于SQLite等文件型数据库）
    "mysql_host": "127.0.0.1", // MySQL主机地址
    "mysql_port": 3306,         // MySQL端口
    "mysql_user": "root",       // MySQL用户名
    "mysql_password": "123456", // MySQL密码
    "mysql_database": "mcp"     // MySQL数据库名
}
```

mysql 模式会连接 mysql 数据库，需要新建一个库，服务启动会自动初始化

sqlite 模式会在服务启动时，自动在 backend 下新建 db 数据库

## 2.4 启动服务

在 backend 目录下

```
python run.py
```

### 3. 前端

frontend 文件夹为前端工程，需要安装 node，编译工具推荐 yarn（npm 也可以）

环境版本说明：

- node: v18.20.4
- yarn: 1.22.15

## 3.1 安装依赖

```
cd frontend
yarn install
```

等待安装成功

## 3.2 启动前端

进入 frontend 文件夹

```
yarn run dev
```

启动后，即可访问前端

默认用户名密码是：admin mcp@12345

启动后会内置示例工具，数据库助手、tavily_search 工具需要配置对应的数据库信息和 key

后端地址配置在 vite.config.ts，前端会把/api 请求，转发到后端服务上

## 3.3 打包

进入 frontend 文件夹

```
yarn run build
```

打包成功后，将生成的 dist 文件夹，放到 backend/文件夹下，即可直接访问后端端口，实现平台预览

## 使用说明

## 配置文件说明

配置文件`backend/config.json`包含以下主要部分：

### 1. cors（跨域资源共享配置）

```json
"cors": {
    "origins": ["*"],           // 允许的来源域，"*"表示允许所有域
    "credentials": true,        // 是否允许发送身份凭证
    "methods": ["*"],           // 允许的HTTP方法，"*"表示允许所有方法
    "headers": ["*"]            // 允许的HTTP头，"*"表示允许所有头信息
}
```

### 2. api（API 配置）

```json
"api": {
    "prefix": "/api",           // API路径前缀
    "title": "Egova AI MCP Server", // API标题
    "version": "1.0.0"          // API版本号
}
```

### 3. server（服务器配置）

```json
"server": {
    "host": "0.0.0.0",          // 服务器绑定地址，0.0.0.0表示监听所有网络接口
    "port": 8002,               // 服务器监听端口
    "debug": true               // 是否开启调试模式
}
```

### 4. mcp（MCP 特定配置）

```json
"mcp": {
    "port": 8002,               // MCP服务端口
    "sse_url": "http://10.4.1.132:8002/sse", // 服务器发送事件(SSE)URL
    "enabled_tools": []         // 启用的工具列表
}
```

### 5. logging（日志配置）

```json
"logging": {
    "level": "info",            // 日志级别
    "backup_count": 7           // 日志备份数量
}
```

### 6. database（数据库配置）

```json
"database": {
    "type": "mysql",            // 数据库类型，支持mysql和sqlite
    "file": "mcp.db",     // 数据库文件（用于SQLite等文件型数据库）
    "mysql_host": "127.0.0.1", // MySQL主机地址
    "mysql_port": 3306,         // MySQL端口
    "mysql_user": "root",       // MySQL用户名
    "mysql_password": "root", // MySQL密码
    "mysql_database": "mcp"     // MySQL数据库名
}
```

## MCP 工具示例说明

系统启动时会自动创建以下 MCP 示例：

### 1. 计算工具 (calculator)

提供基本的数学计算功能，包括加法、乘法和复杂表达式计算。

### 2. 网络搜索工具 (web_search)

提供网络搜索功能，可以从互联网上获取信息和热门话题。

### 3. Tavily 搜索助手

使用 Tavily API 进行实时在线搜索，需要配置 Tavily API 密钥。

### 4. 数据库工具助手

提供数据库操作功能，包括表查询、字段查询和执行 SQL 语句等。需要配置数据库连接参数。

### 自定义 MCP 工具

用户可以通过以下方式自定义 MCP 工具：

1. 编写工具代码
2. 配置所需秘钥和参数
3. 发布为 MCP 服务

具体开发规范请参考示例代码。在代码中使用`${参数名}`格式的占位符，可在运行时由平台自动替换为实际配置的参数值。

## MCP 使用效果

### 效果说明

提问：查询 10 条告警数据的设备编号、告警时间，先通过工具查询告警表是哪个，再用查询 sql 的方法，查询数据。不是查询表字段信息，是查询表中记录的行数据

大模型根据提问和 MCP 工具，自动执行了下面的步骤：

1. 查询出了可以用的 MCP 工具

   - execute_raw_query
   - get_all_tables
   - get_table_columns
   - get_table_data

2. 选择 get_all_tables 工具，查询所有的表数据

   ```json
   [{"name": "com_alarm_data", "comment": "", "CREATE_TIME": "2025-04-10 11:49:07", "UPDATE_TIME": "2025-05-07 13:56:17"}, {"name": "com_alarm_level", "comment": "", "CREATE_TIME": "2024-05-20 17:07:57", "UPDATE_TIME": null}, {"na...
   ```

3. 选择了 com_base_alarm 表

4. 选择 execute_raw_query 工具，编写 sql 查询，从 alarm 表查询 device_id，查询结果是没有该字段

5. 重新选择 get_table_colums 工具，查询 alarm 表有哪些字段

6. 选择 execute_raw_query 工具，编写 sql，从 alarm 表查询 DeviceCode、AlarmTime 字段的数据（因为问题是告警设备编号和时间）

7. 调用图表 mcp 工具，生成 echarts 图表代码，页面上渲染
   ![chat.png](https://img.picui.cn/free/2025/05/14/68242dc44c79e.png)
