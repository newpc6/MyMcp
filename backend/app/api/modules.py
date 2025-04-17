from fastapi import APIRouter, HTTPException
from typing import List

from ..models.modules.schemas import (
    ModuleInfo, ModuleContent, ModuleCreate, ModuleUpdate
)
from ..services.modules.service import ModuleService

router = APIRouter()
module_service = ModuleService()


@router.get("", response_model=List[ModuleInfo])
async def get_modules():
    """获取所有模块信息"""
    return module_service.get_all_modules()


@router.get("/list", response_model=List[str])
async def list_modules():
    """获取所有模块路径列表"""
    return module_service.list_modules()


@router.get("/count")
async def get_module_count():
    """获取模块数量"""
    return {"count": module_service.get_module_count()}


@router.get("/{module_path:path}", response_model=ModuleContent)
async def get_module(module_path: str):
    """获取模块内容"""
    try:
        return module_service.get_module_content(module_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Module not found")


@router.put("/{module_path:path}")
async def update_module(
    module_path: str, 
    module_update: ModuleUpdate
):
    """更新模块内容"""
    try:
        module_service.update_module(
            module_path, 
            module_update.content
        )
        return {"message": "Module updated successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Module not found")


@router.post("")
async def create_module(module_create: ModuleCreate):
    """创建新模块"""
    try:
        module_service.create_module(
            module_create.path, 
            module_create.content
        )
        return {"message": "Module created successfully"}
    except FileExistsError:
        raise HTTPException(status_code=409, detail="Module already exists")


@router.delete("/{module_path:path}")
async def delete_module(module_path: str):
    """删除模块"""
    try:
        module_service.delete_module(module_path)
        return {"message": "Module deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Module not found") 