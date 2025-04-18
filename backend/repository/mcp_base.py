"""
兼容性模块，将导入重定向到app.server.mcp_server

此模块用于向后兼容，新代码应直接使用app.server模块
"""

import os
import sys
import warnings

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

# 发出废弃警告
warnings.warn(
    "repository.mcp_base模块已废弃，请使用app.server.mcp_server模块替代",
    DeprecationWarning,
    stacklevel=2
)

# 从新的位置导入
from app.server.mcp_server import (
    server_instance as mcp,
    add_tool,
    remove_tool,
    get_enabled_tools,
    is_running,
    check_mcp_status,
    start_mcp_server,
    stop_mcp_server,
    restart_mcp_server
)

# 导出接口
__all__ = [
    'mcp',
    'add_tool',
    'remove_tool',
    'get_enabled_tools',
    'is_running',
    'check_mcp_status',
    'start_mcp_server',
    'stop_mcp_server',
    'restart_mcp_server'
] 