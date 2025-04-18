"""
初始化模块，提供仓库功能

MCP服务器会自动扫描这个目录下的所有函数，并将它们注册为工具
不需要任何装饰器，函数会自动注册

如需手动添加工具，请使用下面的导入方式:
from ..mcp_server import add_tool

例如:
from ..mcp_server import add_tool
add_tool(my_function, "工具名称", "工具描述")
"""
