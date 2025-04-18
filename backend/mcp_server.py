"""
MCP服务器启动脚本

此文件用于兼容性，新版本建议直接通过app.server.mcp_server启动
"""

import os
import sys
import warnings

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.server.mcp_server import start_mcp_server

# 发出废弃警告
warnings.warn(
    "mcp_server.py已移动到app/server目录，请使用新路径",
    DeprecationWarning,
    stacklevel=2
)

# 如果直接运行此文件
if __name__ == "__main__":
    start_mcp_server()

