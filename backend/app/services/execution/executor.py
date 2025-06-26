"""
工具执行模块，负责动态调用工具函数
"""
import importlib
from typing import Dict, Any, Callable

from app.models.engine import get_db
from app.models.modules.mcp_tool import McpTool


async def execute_tool_by_name(tool_name: str, params: Dict[str, Any]) -> Any:
    """
    通过工具名称执行工具
    
    Args:
        tool_name: 工具名称
        params: 工具参数
        
    Returns:
        Any: 工具执行结果
    """
    try:
        # 查找工具函数
        tool_func = await _find_tool_function(tool_name)
        if not tool_func:
            return {"error": f"找不到工具: {tool_name}"}
        
        # 执行工具函数
        result = tool_func(**params)
        return result
    except Exception as e:
        return {"error": f"执行失败: {str(e)}"}


async def _find_tool_function(tool_name: str) -> Callable:
    """
    在repository目录中查找指定名称的工具函数
    
    Args:
        tool_name: 工具名称
        
    Returns:
        Callable: 工具函数对象
    """
    with get_db() as db:
        # 查询工具
        tool = db.query(McpTool).filter(McpTool.name == tool_name).first()
        if not tool:
            return None
        
        try:
            # 获取模块路径和函数名
            module_path = tool.module.module_path
            function_name = tool.function_name
            
            # 导入模块
            module = importlib.import_module(module_path)
            
            # 获取函数
            func = getattr(module, function_name)
            return func
        except Exception as e:
            print(f"查找工具函数 {tool_name} 时出错: {str(e)}")
            return None 