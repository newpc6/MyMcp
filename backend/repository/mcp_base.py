from mcp.server.fastmcp import FastMCP
from app.core.config import settings

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 添加backend目录到Python路径
backend_path = os.path.join(project_root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# 创建MCP实例
mcp = FastMCP(
    "egova-ai-mcp-server",
    port=settings.MCP_PORT
)