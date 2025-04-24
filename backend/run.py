import os
import sys

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print(f"当前进程ID: {os.getpid()}")
    from app.server.mcp_server import start_mcp_server    
    # 启动MCP服务器（阻塞调用）
    start_mcp_server()