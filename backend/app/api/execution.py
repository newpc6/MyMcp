from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from ..models.tools.schemas import ToolCall
from ..services.execution.service import ExecutionService

execution_service = ExecutionService()


async def execute_tool(request: Request):
    """执行MCP工具"""
    try:
        data = await request.json()
        tool_call = ToolCall(**data)
        
        result = execution_service.execute_tool(
            tool_call.tool_name,
            tool_call.parameters
        )
        return JSONResponse({"result": result})
    except ValueError as e:
        return JSONResponse({"detail": str(e)}, status_code=404)
    except RuntimeError as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


def get_router():
    """获取执行路由"""
    routes = [
        Route("/", endpoint=execute_tool, methods=["POST"])
    ]
    
    return routes 