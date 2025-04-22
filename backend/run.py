import os
import sys

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print(f"当前进程ID: {os.getpid()}")
    
    # 先导入必要模块，避免循环导入
    from app.main import init_app
    from app.server.mcp_server import start_mcp_server
    
    # 初始化应用
    init_app()
    
    # 启动MCP服务器（阻塞调用）
    start_mcp_server()

    # 等待MCP服务器启动
    # time.sleep(1)
    # mcp_server = get_mcp_server()
    # if not mcp_server:
    #     em_logger.error("MCP服务器启动失败")
    #     sys.exit(1)

    # 运行应用
    # uvicorn.run(
    #     "app.main:app",
    #     host=settings.HOST,
    #     port=settings.PORT,
    #     reload=settings.DEBUG,
    #     reload_dirs=[
    #         os.path.dirname(os.path.abspath(__file__))
    #     ],  # 仅监视backend目录
    # ) 