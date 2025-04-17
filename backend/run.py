import uvicorn
import os
import sys
from app.core.config import settings
from app.main import init_app
import threading
from mcp_server import start_mcp_server

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    mcp_thread = threading.Thread(target=start_mcp_server)
    mcp_thread.start()
    # 初始化应用，包括数据库初始化
    app = init_app()
    
    # 运行应用
    uvicorn.run(
        "app.main:app",  # 使用导入字符串格式 "module:app_instance"
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG
    ) 