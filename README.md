# MyMcp

## 交流群

qq 群：979958989
加群更及时交流、讨论

![qq-group.png](https://img.picui.cn/free/2025/07/09/686e35890b48d.png)

## 介绍

开源介绍 https://blog.csdn.net/u012327423/article/details/147531100

## 软件架构

软件架构说明

## 模块说明

### 登录页面

![login-v2.jpg](https://img.picui.cn/free/2025/07/09/686e3587a0106.jpg)

### MCP 模板广场

![mcp-squera-v2.jpg](https://img.picui.cn/free/2025/07/09/686e358951af2.jpg)

#### MCP 模板-详情

![detail-v2.jpg](https://img.picui.cn/free/2025/07/09/686e35867a75d.jpg)

#### MCP 模板-工具测试

展示了

- 工具列表
- 测试参数（模板中如果配置了，可以配置参数是否必填）
- 工具执行（如果配置了工具函数参数，需要填写）
- 工具函数代码（了解工具执行原理）

![tool-test.jpg](https://img.picui.cn/free/2025/07/09/686e3589229a2.jpg)

#### MCP 模板-参数配置

![template-params.jpg](https://img.picui.cn/free/2025/07/09/686e36be6b488.jpg)

#### MCP 模板-发布服务

![template-publish.jpg](https://img.picui.cn/free/2025/07/09/686e36be074a0.jpg)

#### MCP 模板-代码编辑

![template-code.jpg](https://img.picui.cn/free/2025/07/09/686e36be029a6.jpg)

### MCP 服务

支持管理内置服务
![mcp-service-v2-1.jpg](https://img.picui.cn/free/2025/07/09/686e36bf35f74.jpg)

支持新增第三方 http sse 地址

![mcp-service-v2-third.jpg](https://img.picui.cn/free/2025/07/09/686e36bd37291.jpg)

### MCP 统计

![mcp-stat-v2-1.jpg](https://img.picui.cn/free/2025/07/09/686e379a27de3.jpg)
![mcp-stat-v2-2.jpg](https://img.picui.cn/free/2025/07/09/686e379996aee.jpg)
![mcp-stat-v2-3.jpg](https://img.picui.cn/free/2025/07/09/686e379a642c5.jpg)

### 用户管理

![user-v2.jpg](https://img.picui.cn/free/2025/07/09/686e379a4bddb.jpg)

### 租户管理

## 系统管理

![system-v2.jpg](https://img.picui.cn/free/2025/07/09/686e3820ef2d2.jpg)

### 定时任务

![system-schedule-v2.jpg](https://img.picui.cn/free/2025/07/09/686e3821080d2.jpg)

### python 包管理

还有点小问题，未完全实现
![python-install-2.jpg](https://img.picui.cn/free/2025/07/09/686e3820dab5d.jpg)


## 20250711新增功能

### MCP服务秘钥管理

#### 功能概述
新增MCP服务秘钥配置功能，支持对API访问进行权限控制和用量管理。

#### 秘钥管理界面
![mcp-secret-manage-1.jpg](https://cdn.picui.cn/vip/2025/07/11/6870c42238f58.jpg)

#### 秘钥详情查看
![mcp-secret-manage-2.jpg](https://cdn.picui.cn/vip/2025/07/11/6870c4219145c.jpg)

#### 秘钥创建与编辑
支持新增和编辑MCP服务访问秘钥，配置访问权限和用量限制。

![mcp-secret-add-2.jpg](https://cdn.picui.cn/vip/2025/07/11/6870c421aab03.jpg)
![mcp-secret-add-3.jpg](https://cdn.picui.cn/vip/2025/07/11/6870c4222c549.jpg)
![mcp-secret-add-success.jpg](https://cdn.picui.cn/vip/2025/07/11/6870c4221b567.jpg)

#### 访问记录统计
提供详细的秘钥使用记录和统计信息，便于监控和管理API使用情况。

![mcp-secret-access-1.jpg](https://cdn.picui.cn/vip/2025/07/11/6870c49b3c878.jpg)

#### 客户端测试示例

**未使用秘钥（401错误）**
当客户端未提供有效秘钥时，系统返回401未授权错误。

![mcp-secret-401.jpg](https://cdn.picui.cn/vip/2025/07/11/6870c49b0cafa.jpg)

**超出当日限额**
当秘钥使用次数超过设定的每日限额时，系统会拒绝请求并提示超出限额。

![mcp-secret-out-of-limit.jpg](https://cdn.picui.cn/vip/2025/07/11/6870c49b4cfdd.jpg)

## 临时体验地址

http://111.4.141.154:7002

guest/123456（只能看公开的，和自己的）

admin/mcp@12345（能管理所有的）

## 安装教程

### 1. 拉取项目

拉取工程到本地

### 2. 后端

## 2.1 创建 python 环境

以 conda 为例，创建 conda 环境，命名可以是 mcp。python 版本推荐 3.11

等待创建成功后

切换为刚创建的 conda 环境

```
conda activate mcp
```

进入后端目录，安装 python 依赖，推荐清华源

```
cd backend
pip install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
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
    "prefix": "/api/v1/mcp",  // API路径前缀
    "title": "MCP Server",    // API标题
    "version": "1.0.0"        // API版本号
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
