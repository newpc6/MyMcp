from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.server.mcp_server import (
    add_tool, remove_tool, restart_mcp_server, check_mcp_status, get_enabled_tools
)
from ..core.config import settings

router = APIRouter()


class ToolLoadRequest(BaseModel):
    """加载工具请求模型"""
    module_path: str  # 模块路径，例如 "repository.demo_tool"
    function_name: str  # 函数名称
    tool_name: Optional[str] = None  # 可选的工具名称，默认使用函数名
    description: Optional[str] = None  # 可选的工具描述


class ToolRemoveRequest(BaseModel):
    """移除工具请求模型"""
    tool_name: str  # 工具名称


class UpdateSSEUrlRequest(BaseModel):
    """更新SSE URL请求模型"""
    sse_url: str  # 新的SSE URL


@router.post("/load_tool")
async def load_tool(request: ToolLoadRequest):
    """动态加载工具"""
    try:
        # 动态导入模块
        import importlib
        try:
            module = importlib.import_module(request.module_path)
        except ImportError as e:
            raise HTTPException(status_code=404, detail=f"模块 {request.module_path} 导入失败: {str(e)}")
        
        # 获取函数
        if not hasattr(module, request.function_name):
            raise HTTPException(status_code=404, detail=f"函数 {request.function_name} 在模块 {request.module_path} 中不存在")
        
        func = getattr(module, request.function_name)
        
        # 添加为工具
        add_tool(
            func=func,
            name=request.tool_name,
            doc=request.description
        )
        
        return {
            "message": f"工具 {request.tool_name or request.function_name} 已成功加载",
            "tool_name": request.tool_name or request.function_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载工具失败: {str(e)}")


@router.post("/unload_tool")
async def unload_tool(request: ToolRemoveRequest):
    """动态卸载工具"""
    try:
        success = remove_tool(request.tool_name)
        if success:
            return {"message": f"工具 {request.tool_name} 已成功卸载"}
        else:
            raise HTTPException(status_code=404, detail=f"工具 {request.tool_name} 不存在或卸载失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"卸载工具失败: {str(e)}")


@router.post("/restart")
async def restart_service():
    """重启MCP服务"""
    try:
        success = restart_mcp_server()
        if success:
            return {"message": "MCP服务已成功重启"}
        else:
            raise HTTPException(status_code=500, detail="MCP服务重启失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重启服务失败: {str(e)}")


@router.get("/status")
async def get_status():
    """获取MCP服务状态"""
    try:
        status = check_mcp_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")


@router.get("/enabled_tools")
async def enabled_tools():
    """获取当前启用的工具列表"""
    try:
        tools = get_enabled_tools()
        return {"enabled_tools": tools, "count": len(tools)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取启用工具列表失败: {str(e)}")


@router.put("/sse_url")
async def update_sse_url(request: UpdateSSEUrlRequest):
    """更新MCP SSE URL"""
    try:
        # 更新配置
        settings.MCP_SSE_URL = request.sse_url
        
        # 返回更新后的状态
        return {
            "message": "MCP SSE URL已更新",
            "new_sse_url": settings.MCP_SSE_URL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新SSE URL失败: {str(e)}") 