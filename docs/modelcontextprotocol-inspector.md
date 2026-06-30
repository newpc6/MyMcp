运行 MCP Inspector

要运行 MCP Inspector，可以使用 npx 命令从 MCP 服务器仓库中直接运行，而无需克隆 MCP Inspector 仓库。例如，如果你的服务器构建在 build/index.js 中，可以使用以下命令：

npx @modelcontextprotocol/inspector node build/index.js
你可以传递参数和环境变量给 MCP 服务器。参数直接传递给服务器，而环境变量可以使用 -e 标志设置：

# 仅传递参数
npx @modelcontextprotocol/inspector node build/index.js arg1 arg2

# 仅传递环境变量
npx @modelcontextprotocol/inspector -e key=value -e key2=$VALUE2 node build/index.js

# 同时传递环境变量和参数
npx @modelcontextprotocol/inspector -e key=value -e key2=$VALUE2 node build/index.js arg1 arg2

# 使用 -- 分隔 inspector 标志和服务器参数
npx @modelcontextprotocol/inspector -e key=$VALUE -- node build/index.js -e server-flag
MCP Inspector 运行 MCP Inspector 客户端 UI（默认端口 6274）和 MCP Proxy 服务器（默认端口 6277）。你可以在浏览器中打开 MCP Inspector 客户端 UI 来使用 Inspector。