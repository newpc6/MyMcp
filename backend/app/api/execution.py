from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from ..models.tools.schemas import ToolCall
from ..services.execution.service import ExecutionService

router = APIRouter()
execution_service = ExecutionService()


@router.post("")
async def execute_tool(tool_call: ToolCall) -> Dict[str, Any]:
    """执行MCP工具"""
    try:
        result = execution_service.execute_tool(
            tool_call.tool_name,
            tool_call.parameters
        )
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) 