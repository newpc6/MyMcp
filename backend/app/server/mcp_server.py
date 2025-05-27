import json
import os
import sys
import time
import inspect
from typing import Callable, Dict, Any, Optional, List
import threading

import anyio
from sqlalchemy import update
import uvicorn

from app.models.modules.mcp_services import McpService
from app.models.engine import get_db

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
uni_server = None

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

            return True
        else:
            em_logger.warning(f"工具 {tool_name} 不存在，无需移除")
            return False
    except Exception as e:
        em_logger.error(f"移除工具 {tool_name} 时出错: {str(e)}")
        return False

def get_service_by_id(id: int):
    """获取服务实例"""
    with get_db() as db:
        query = db.query(McpService)
        query = query.filter(McpService.id == id)
        return query.first()
    

def update_service_params(id: int, config_params: Dict[str, Any]):
    """更新服务参数"""
    if server_instance is None:
        em_logger.warning("MCP服务器尚未启动，无法更新服务参数")
        return False
    
    with get_db() as db:
        db.execute(
            update(McpService)
            .where(McpService.id == id)
            .values(config_params=json.dumps(config_params))
        )
        db.commit()        
        return True

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
        "port": settings.PORT,
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


def get_mcp_server():
    main_thread = threading.main_thread()
    current_thread = threading.current_thread()
    global server_instance
    em_logger.info(
        "获取MCP变量，主线程：%s 当前线程：%s，是否是主线程：%s， "
        "进程ID：%s， server_instance：%s",
        main_thread, current_thread, main_thread == current_thread,
        os.getpid(), server_instance is not None
    )
    return server_instance


async def run_sse_async(app) -> None:
    """Run the server using SSE transport."""
    global uni_server
    await uni_server.serve()


def start_mcp_server():
    """启动MCP服务器"""
    global server_instance

    # 导入中间件和路由配置 - 在函数内部导入，避免循环导入
    from app.middleware.logging_middleware import APILoggingMiddleware
    from app.middleware.tool_execution_middleware import ToolExecutionMiddleware
    from app.models.engine import init_db
    init_db()

    global server_instance
    # 创建FastMCP实例
    server_instance = FastMCP(
        name="MCP Server",
        host=settings.HOST,
        port=settings.PORT,
    )

    # 创建SSE应用并配置中间件
    app = server_instance.sse_app()
    
    # 输出CORS配置信息
    em_logger.info(
        f"CORS配置: allow_origins={settings.CORS_ORIGINS}, "
        f"allow_credentials={settings.CORS_CREDENTIALS}"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    # 添加日志中间件
    app.add_middleware(APILoggingMiddleware)
    # 添加工具执行中间件
    app.add_middleware(ToolExecutionMiddleware)

    # 在实例创建后导入和注册路由，避免循环导入
    from app.api.urls import get_router
    # 使用Starlette Router对象代替FastAPI应用
    get_router(app)
    # 保存服务器实例
    # server_instance = server
    em_logger.info(f"启动 {settings.API_TITLE} v{settings.API_VERSION}")
        
    global uni_server
    config = uvicorn.Config(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
    uni_server = uvicorn.Server(config)
    from app.services.mcp_service.service_manager import service_manager
    service_manager.init_app(app)

    # 启动统计数据定时任务
    try:
        from app.services.schedule_service.statistics_task import (
            start_statistics_scheduler
        )
        start_statistics_scheduler()
        em_logger.info("统计数据定时任务已启动")
    except Exception as e:
        em_logger.error(f"启动统计数据定时任务时出错: {str(e)}")

    # 启动缓存清理定时任务
    try:
        from app.services.schedule_service import start_cache_clean_scheduler
        start_cache_clean_scheduler()
        em_logger.info("缓存清理定时任务已启动")
    except Exception as e:
        em_logger.error(f"启动缓存清理定时任务时出错: {str(e)}")

    # 启动服务器
    if threading.current_thread() is not threading.main_thread():
        import time
        time.sleep(0.5)  # 给其他线程一点时间来访问server_instance

    # 这是阻塞调用
    try:
        em_logger.info(f"启动MCP服务器... 端口: {settings.PORT}")
        anyio.run(run_sse_async, app)
    except Exception as e:
        em_logger.error(f"启动MCP服务器时出错: {str(e)}")
    return server_instance


# 如果直接运行此文件
if __name__ == "__main__":
    start_mcp_server()
