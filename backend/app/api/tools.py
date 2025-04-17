from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..models.tools.schemas import (
    ToolInfo, ToolContent, ToolCreate, ToolUpdate
)
from ..services.tools.service import ToolService

router = APIRouter()
tool_service = ToolService()


@router.get("", response_model=List[ToolInfo])
async def get_tools():
    """获取所有工具信息"""
    return tool_service.get_all_tools()


@router.get("/list", response_model=List[Any])
async def list_tools():
    """获取所有工具信息列表"""
    return tool_service.list_tools()


@router.get("/info/{tool_name}", response_model=Dict[str, Any])
async def get_tool_info(tool_name: str):
    """获取特定工具信息"""
    try:
        return tool_service.get_tool_info(tool_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{tool_path:path}", response_model=ToolContent)
async def get_tool(tool_path: str):
    """获取工具内容"""
    try:
        return tool_service.get_tool_content(tool_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="工具未找到")
    except PermissionError:
        raise HTTPException(status_code=403, detail="没有权限访问该工具")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工具内容失败: {str(e)}")


@router.put("/{tool_path:path}")
async def update_tool(tool_path: str, tool_update: ToolUpdate):
    """更新工具内容"""
    try:
        tool_service.update_tool(tool_path, tool_update.content)
        return {"message": "Tool updated successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tool not found")


@router.post("")
async def create_tool(tool_create: ToolCreate):
    """创建新工具"""
    try:
        tool_service.create_tool(tool_create.path, tool_create.content)
        return {"message": "Tool created successfully"}
    except FileExistsError:
        raise HTTPException(status_code=409, detail="Tool already exists")


@router.delete("/{tool_path:path}")
async def delete_tool(tool_path: str):
    """删除工具"""
    try:
        tool_service.delete_tool(tool_path)
        return {"message": "Tool deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tool not found") 