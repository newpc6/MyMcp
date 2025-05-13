# MyMcp

## 介绍
开源介绍 https://blog.csdn.net/u012327423/article/details/147531100

## 软件架构
软件架构说明

## 模块说明
### MCP广场
![](https://img.remit.ee/api/file/AgACAgUAAyEGAASHRsPbAAIKLmgjSUf-awc7pOFluacXGKLBtIeaAAJJxDEbmboZVXNO4KdTf63RAQADAgADdwADNgQ.jpg)

#### MCP工具-测试
[![tool1.jpg](https://img.picui.cn/free/2025/05/13/68234a4668f1d.jpg)](https://img.picui.cn/free/2025/05/13/68234a4668f1d.jpg)

#### MCP服务发布-参数配置
[![tool2.jpg](https://img.picui.cn/free/2025/05/13/68234a466f775.jpg)](https://img.picui.cn/free/2025/05/13/68234a466f775.jpg)

### MCP服务
![](https://img.remit.ee/api/file/AgACAgUAAyEGAASHRsPbAAIKL2gjSe1pWFa6MYOfRk3gpqW4y7xKAAJLxDEbmboZVS9Rh0LI4QQgAQADAgADdwADNgQ.jpg)

### MCP统计
[![statistics.jpg](https://img.picui.cn/free/2025/05/13/68234a467204f.jpg)](https://img.picui.cn/free/2025/05/13/68234a467204f.jpg)

## 安装教程

### 1. 拉取项目
拉取工程到本地

### 2. 后端
## 2.1 创建python环境
以conda为例，创建conda环境，命名可以是mcp。python版本推荐3.11

等待创建成功后

切换为刚创建的conda环境
```
conda activate mcp-test
```

进入后端目录，安装python依赖，推荐清华源
```
cd backend
pip install -r .\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 2.2 调整配置文件
新建配置文件，在backend路径下，复制config.jsonbak为config.json

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

### 2. api（API配置）
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

### 4. mcp（MCP特定配置）
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
    "mysql_password": "123456", // MySQL密码
    "mysql_database": "mcp"     // MySQL数据库名
}
```

mysql模式会连接mysql数据库，需要新建一个库，服务启动会自动初始化

sqlite模式会在服务启动时，自动在backend下新建db数据库

## 2.4 启动服务
在backend目录下
```
python run.py
```

### 3. 前端
frontend文件夹为前端工程，需要安装node，编译工具推荐yarn（npm也可以）

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
进入frontend文件夹
```
yarn run dev
```

启动后，即可访问前端

默认用户名密码是：admin mcp@12345

启动后会内置示例工具，数据库助手、tavily_search工具需要配置对应的数据库信息和key

后端地址配置在vite.config.ts，前端会把/api请求，转发到后端服务上

## 3.3 打包
进入frontend文件夹
```
yarn run build
```

打包成功后，将生成的dist文件夹，放到backend/文件夹下，即可直接访问后端端口，实现平台预览

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

### 2. api（API配置）
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

### 4. mcp（MCP特定配置）
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

## MCP工具示例说明

系统启动时会自动创建以下MCP示例：

### 1. 计算工具 (calculator)
提供基本的数学计算功能，包括加法、乘法和复杂表达式计算。

### 2. 网络搜索工具 (web_search)
提供网络搜索功能，可以从互联网上获取信息和热门话题。

### 3. Tavily搜索助手
使用Tavily API进行实时在线搜索，需要配置Tavily API密钥。

### 4. 数据库工具助手
提供数据库操作功能，包括表查询、字段查询和执行SQL语句等。需要配置数据库连接参数。

### 自定义MCP工具

用户可以通过以下方式自定义MCP工具：
1. 编写工具代码
2. 配置所需秘钥和参数
3. 发布为MCP服务

具体开发规范请参考示例代码。在代码中使用`${参数名}`格式的占位符，可在运行时由平台自动替换为实际配置的参数值。
