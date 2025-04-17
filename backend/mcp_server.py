import os
import sys
import importlib
import signal
import time

# 导入配置和基础模块
from app.core.config import settings
from repository.mcp_base import mcp

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


# MCP服务器实例
server_instance = None


# 动态导入repository目录下的所有模块
def import_all_from_repository():
    # 获取repository目录
    repo_dir = os.path.join(current_dir, 'repository')
    
    # 首先导入mcp_base
    try:
        importlib.import_module('repository.mcp_base')
        print("成功导入基础模块: repository.mcp_base")
    except Exception as e:
        print(f"导入基础模块失败: {e}")
        return
    
    # 获取repository目录下其他的py文件
    for file in os.listdir(repo_dir):
        if (file.endswith('.py') and 
                file != '_init_.py' and 
                file != '__init__.py' and
                file != 'mcp_base.py'):
            module_name = file[:-3]  # 去掉.py后缀
            module_path = f'repository.{module_name}'
            try:
                importlib.import_module(module_path)
                print(f"成功导入模块: {module_path}")
            except Exception as e:
                print(f"导入模块 {module_path} 失败: {e}")


def start_mcp_server():
    global server_instance
    
    # 导入repository中的所有模块
    import_all_from_repository()
    
    # 启动服务器
    print(f"启动MCP服务器... 端口: {settings.MCP_PORT}")
    server_instance = mcp.run(
        transport='sse'
    )
    return server_instance


def stop_mcp_server():
    global server_instance
    if server_instance:
        print("停止MCP服务器...")
        server_instance.stop()
        server_instance = None


def restart_mcp_server():
    print("重启MCP服务器...")
    stop_mcp_server()
    time.sleep(1)  # 等待服务器完全停止
    return start_mcp_server()


# 处理终止信号
def signal_handler(sig, frame):
    print("接收到终止信号，正在关闭服务器...")
    stop_mcp_server()
    sys.exit(0)


# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# 如果直接运行此文件
if __name__ == "__main__":
    start_mcp_server()

