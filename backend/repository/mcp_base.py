from mcp.server.fastmcp import FastMCP
from app.core.config import settings

import os
import sys
import inspect
from typing import Callable, Dict, Any, Optional, List

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

# 以下为新增部分

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
    tool_name = name or func.__name__
    tool_doc = doc or inspect.getdoc(func) or ""
    
    # 检查工具是否已存在
    try:
        existing_tools = {tool.name for tool in mcp._tool_manager.list_tools()}
        if tool_name in existing_tools:
            print(f"工具 {tool_name} 已存在，将先移除")
            remove_tool(tool_name)
    except Exception as e:
        print(f"检查现有工具时出错: {e}")
    
    # 使用mcp的tool装饰器添加工具
    mcp.tool(name=tool_name, description=tool_doc)(func)
    
    # 存储工具信息，用于重启时
    _manually_added_tools.append({
        "func": func,
        "name": tool_name,
        "doc": tool_doc
    })
    
    print(f"已成功添加工具: {tool_name}")
    return func  # 返回函数便于链式调用


def remove_tool(tool_name: str) -> bool:
    """
    动态移除MCP工具
    
    Args:
        tool_name: 要移除的工具名称
        
    Returns:
        bool: 是否成功移除
    """
    try:
        # 直接从工具管理器中移除
        if (hasattr(mcp._tool_manager, "_tools") 
                and tool_name in mcp._tool_manager._tools):
            del mcp._tool_manager._tools[tool_name]
            print(f"已从工具管理器中移除工具: {tool_name}")
            
            # 从手动添加列表中移除
            global _manually_added_tools
            _manually_added_tools = [
                t for t in _manually_added_tools if t["name"] != tool_name
            ]
            
            return True
        else:
            print(f"工具 {tool_name} 不存在，无需移除")
            return False
    except Exception as e:
        print(f"移除工具 {tool_name} 时出错: {e}")
        return False


def restart_mcp() -> bool:
    """
    重新启动MCP服务
    
    Returns:
        bool: 重启是否成功
    """
    try:
        # 保存当前所有手动添加的工具列表
        tools_to_reload = _manually_added_tools.copy()
        
        global mcp
        # 关闭当前MCP实例
        mcp.stop()
        
        # 重新创建MCP实例
        mcp = FastMCP(
            "egova-ai-mcp-server",
            port=settings.MCP_PORT
        )
        
        # 重新加载所有手动添加的工具
        for tool_info in tools_to_reload:
            add_tool(
                func=tool_info["func"],
                name=tool_info["name"],
                doc=tool_info["doc"]
            )
        
        # 重新启动MCP服务
        mcp.start()
        
        print("MCP服务已成功重启")
        return True
    except Exception as e:
        print(f"重启MCP服务时出错: {e}")
        return False


def get_enabled_tools() -> List[str]:
    """
    获取当前启用的工具列表
    
    Returns:
        List[str]: 启用的工具名称列表
    """
    try:
        return [tool.name for tool in mcp._tool_manager.list_tools()]
    except Exception as e:
        print(f"获取启用工具列表时出错: {e}")
        return []


def is_running() -> bool:
    """
    检查MCP服务是否正在运行
    
    Returns:
        bool: 服务是否正在运行
    """
    try:
        # 逐层检查各种可能的运行状态属性
        if hasattr(mcp, 'is_running'):
            return mcp.is_running()
        elif hasattr(mcp, '_server') and hasattr(mcp._server, 'is_running'):
            return mcp._server.is_running
        elif hasattr(mcp, '_server') and hasattr(mcp._server, 'running'):
            return mcp._server.running
        
        # 如果以上都没有，检查是否有工具注册作为后备策略
        tools = get_enabled_tools()
        return len(tools) > 0
    except Exception as e:
        print(f"检查MCP运行状态时出错: {e}")
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