"""
工具执行相关API
"""
import importlib
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpTool
from app.services.execution.executor import execute_tool_by_name


async def execute_tool(request: Request):
    """
    执行指定工具
    
    Args:
        tool_name: 工具名称
        params: 工具参数
    """
    tool_name = request.path_params["tool_name"]
    params = await request.json()
    
    try:
        result = await execute_tool_by_name(tool_name, params)
        if "error" in result:
            return JSONResponse({"detail": result["error"]}, status_code=400)
        return JSONResponse({"result": result})
    except Exception as e:
        return JSONResponse({"detail": f"执行失败: {str(e)}"}, status_code=500)


async def execute_tool_by_id(request: Request):
    """
    根据ID执行MCP工具
    
    Args:
        tool_id: 工具ID
        params: 工具参数
    """
    tool_id = int(request.path_params["tool_id"])
    params = await request.json()
    
    try:
        with get_db() as db:
            # 从数据库获取工具信息
            tool = db.query(McpTool).filter(McpTool.id == tool_id).first()
            if not tool:
                return JSONResponse({"detail": "工具不存在"}, status_code=404)
            
            # 获取模块和函数名
            module_path = tool.module.module_path
            function_name = tool.function_name
            
            # 动态导入模块
            module = importlib.import_module(module_path)
            # 获取函数对象
            func = getattr(module, function_name)
            
            # 执行函数
            result = func(**params)
            
            # 返回结果
            return JSONResponse({"result": result})
    except Exception as e:
        return JSONResponse({"detail": f"执行失败: {str(e)}"}, status_code=500)


def get_router():
    """获取工具执行路由"""
    routes = [
        Route("/{tool_name}", endpoint=execute_tool, methods=["POST"]),
        Route("/tool/{tool_id}", endpoint=execute_tool_by_id, methods=["POST"])
    ]
    
    return routes