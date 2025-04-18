import os
import sys
import importlib
import signal
import time
import inspect
from typing import Callable, Dict, Any, Optional, List

# 导入配置和基础模块
from ..core.config import settings
from ..utils.logging import em_logger
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

# 添加当前目录到路径
current_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, current_dir)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# MCP服务器实例
server_instance = None

# 存储已手动添加的工具，用于重启服务时重新加载
_manually_added_tools: List[Dict[str, Any]] = []


def add_tool(
    func: Callable, 
    name: Optional[str] = None, 
    doc: Optional[str] = None
) -> None:
    """
    动态添加MCP工具
    
    Args:
        func: 要添加为工具的函数
        name: 工具名称，如果不提供则使用函数名
        doc: 工具文档，如果不提供则使用函数文档
    """
    if server_instance is None:
        em_logger.warning("MCP服务器尚未启动，无法添加工具")
        return func
        
    tool_name = name or func.__name__
    tool_doc = doc or inspect.getdoc(func) or ""
    
    # 检查工具是否已存在
    try:
        existing_tools = {
            tool.name for tool in server_instance._tool_manager.list_tools()
        }
        if tool_name in existing_tools:
            em_logger.warning(f"工具 {tool_name} 已存在，将先移除")
            remove_tool(tool_name)
    except Exception as e:
        em_logger.error(f"检查现有工具时出错: {str(e)}")
    
    # 使用mcp的tool装饰器添加工具
    server_instance.tool(name=tool_name, description=tool_doc)(func)
    
    # 存储工具信息，用于重启时
    _manually_added_tools.append({
        "func": func,
        "name": tool_name,
        "doc": tool_doc
    })
    
    em_logger.info(f"已成功添加工具: {tool_name}")
    return func  # 返回函数便于链式调用


def remove_tool(tool_name: str) -> bool:
    """
    动态移除MCP工具
    
    Args:
        tool_name: 要移除的工具名称
        
    Returns:
        bool: 是否成功移除
    """
    if server_instance is None:
        em_logger.warning("MCP服务器尚未启动，无法移除工具")
        return False
        
    try:
        # 直接从工具管理器中移除
        if (hasattr(server_instance._tool_manager, "_tools") 
                and tool_name in server_instance._tool_manager._tools):
            del server_instance._tool_manager._tools[tool_name]
            em_logger.info(f"已从工具管理器中移除工具: {tool_name}")
            
            # 从手动添加列表中移除
            global _manually_added_tools
            _manually_added_tools = [
                t for t in _manually_added_tools if t["name"] != tool_name
            ]
            
            return True
        else:
            em_logger.warning(f"工具 {tool_name} 不存在，无需移除")
            return False
    except Exception as e:
        em_logger.error(f"移除工具 {tool_name} 时出错: {str(e)}")
        return False


def get_enabled_tools() -> List[str]:
    """
    获取当前启用的工具列表
    
    Returns:
        List[str]: 启用的工具名称列表
    """
    if server_instance is None:
        return []
        
    try:
        return [
            tool.name for tool in server_instance._tool_manager.list_tools()
        ]
    except Exception as e:
        em_logger.error(f"获取启用工具列表时出错: {str(e)}")
        return []


def is_running() -> bool:
    """
    检查MCP服务是否正在运行
    
    Returns:
        bool: 服务是否正在运行
    """
    if server_instance is None:
        return False
        
    try:
        # 逐层检查各种可能的运行状态属性
        if hasattr(server_instance, 'is_running'):
            return server_instance.is_running()
        elif (hasattr(server_instance, '_server') and 
              hasattr(server_instance._server, 'is_running')):
            return server_instance._server.is_running
        elif (hasattr(server_instance, '_server') and 
              hasattr(server_instance._server, 'running')):
            return server_instance._server.running
        
        # 如果以上都没有，检查是否有工具注册作为后备策略
        tools = get_enabled_tools()
        return len(tools) > 0
    except Exception as e:
        em_logger.error(f"检查MCP运行状态时出错: {str(e)}")
        return False


def check_mcp_status() -> Dict[str, Any]:
    """
    检查MCP服务状态
    
    Returns:
        Dict: 包含状态信息的字典
    """
    status = {
        "port": settings.MCP_PORT,
        "sse_url": settings.MCP_SSE_URL,
        "enabled_tools_count": 0,
        "enabled_tools": []
    }
    
    try:
        # 获取工具列表
        tools = get_enabled_tools()
        status["enabled_tools"] = tools
        status["enabled_tools_count"] = len(tools)
        
        # 检查运行状态
        status["running"] = is_running()
    except Exception as e:
        status["error"] = str(e)
        status["running"] = False
    
    return status


# 用于自动注册仓库中的函数为工具
def register_repository_functions():
    # 获取repository目录
    repo_dir = os.path.join(current_dir, 'repository')
    
    # 导入所有模块
    for file in os.listdir(repo_dir):
        if (file.endswith('.py') and 
                file != '_init_.py' and 
                file != '__init__.py' and
                file != 'mcp_base.py'):
            module_name = file[:-3]  # 去掉.py后缀
            module_path = f'repository.{module_name}'
            try:
                module = importlib.import_module(module_path)
                em_logger.info(f"成功导入模块: {module_path}")
                
                # 遍历模块中的所有函数
                for name, func in inspect.getmembers(
                    module, inspect.isfunction
                ):
                    # 过滤出该模块定义的函数(而不是导入的函数)
                    if func.__module__ == module_path:
                        # 获取函数文档
                        doc = inspect.getdoc(func)
                        # 检查是否已经通过其他方式注册
                        if not any(
                            t['func'] == func for t in _manually_added_tools
                        ):
                            # 注册为工具
                            add_tool(func, name, doc)
                
            except Exception as e:
                em_logger.error(f"导入模块 {module_path} 失败: {str(e)}")


def stop_mcp_server():
    global server_instance
    if server_instance:
        try:
            server_instance.stop()
            server_instance = None
            em_logger.info("已停止MCP服务器")
            return True
        except Exception as e:
            em_logger.error(f"停止MCP服务器时出错: {str(e)}")
            return False
    return False


def restart_mcp_server():
    em_logger.info("正在重启MCP服务器...")
    stop_mcp_server()
    time.sleep(1)  # 等待资源释放
    start_mcp_server()
    em_logger.info("MCP服务器已重新启动")
    return True


def signal_handler(sig, frame):
    em_logger.info("接收到终止信号，正在关闭MCP服务器...")
    stop_mcp_server()
    sys.exit(0)


def start_mcp_server():
    global server_instance
    
    # 创建FastMCP实例
    server = FastMCP(
        name="MCP Server",
        host=settings.HOST,
        port=settings.MCP_PORT,
    )
    
    # 保存服务器实例
    server_instance = server
    
    # 创建SSE应用并配置中间件
    app = server.sse_app()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    # 自动注册仓库中的函数
    register_repository_functions()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务器
    em_logger.info(f"启动MCP服务器... 端口: {settings.MCP_PORT}")
    server_instance.run(transport='sse')
    return server_instance


# 如果直接运行此文件
if __name__ == "__main__":
    start_mcp_server() 