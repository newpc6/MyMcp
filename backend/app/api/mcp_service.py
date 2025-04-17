from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..models.protocols.schemas import McpServiceInfo, McpServiceAction, McpServiceActionResult
from ..services.mcp.service import McpServiceManager

router = APIRouter()
service_manager = McpServiceManager()


@router.get("/", response_model=McpServiceInfo)
async def get_service_info():
    """
    获取MCP服务状态信息
    """
    try:
        return service_manager.get_service_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=McpServiceActionResult)
async def control_service(action: McpServiceAction):
    """
    控制MCP服务（启动、停止、重启）
    """
    try:
        if action.action == "start":
            return service_manager.start_service()
        elif action.action == "stop":
            return service_manager.stop_service()
        elif action.action == "restart":
            return service_manager.restart_service()
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的操作: {action.action}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 