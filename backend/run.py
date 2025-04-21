import os
import uvicorn
import sys
import time
import threading
from app.core.config import settings
from app.server.mcp_server import start_mcp_server, get_mcp_server
from app.utils.logging import em_logger


# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print(f"当前进程ID: {os.getpid()}")
    mcp_thread = threading.Thread(target=start_mcp_server)
    mcp_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
    mcp_thread.start()

    # 等待MCP服务器启动
    time.sleep(1)
    mcp_server = get_mcp_server()
    if not mcp_server:
        em_logger.error("MCP服务器启动失败")
        sys.exit(1)

    # 运行应用
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[
            os.path.dirname(os.path.abspath(__file__))
        ],  # 仅监视backend目录
    ) 