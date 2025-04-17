from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..models.resources.schemas import (
    ResourceInfo, ResourceContent, ResourceCreate, ResourceUpdate
)
from ..services.resources.service import ResourceService

router = APIRouter()
resource_service = ResourceService()


@router.get("", response_model=List[ResourceInfo])
async def get_resources():
    """获取所有资源信息"""
    return resource_service.get_all_resources()


@router.get("/list", response_model=List[str])
async def list_resources():
    """获取所有资源路径列表"""
    return resource_service.list_resources()


@router.get("/info/{resource_path:path}", response_model=Dict[str, Any])
async def get_resource_info(resource_path: str):
    """获取特定资源信息"""
    try:
        return resource_service.get_resource_info(resource_path)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{resource_path:path}", response_model=ResourceContent)
async def get_resource(resource_path: str):
    """获取资源内容"""
    try:
        return resource_service.get_resource_content(resource_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resource not found")


@router.put("/{resource_path:path}")
async def update_resource(
    resource_path: str, 
    resource_update: ResourceUpdate
):
    """更新资源内容"""
    try:
        resource_service.update_resource(
            resource_path, 
            resource_update.content
        )
        return {"message": "Resource updated successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resource not found")


@router.post("")
async def create_resource(resource_create: ResourceCreate):
    """创建新资源"""
    try:
        resource_service.create_resource(
            resource_create.path, 
            resource_create.content
        )
        return {"message": "Resource created successfully"}
    except FileExistsError:
        raise HTTPException(status_code=409, detail="Resource already exists")


@router.delete("/{resource_path:path}")
async def delete_resource(resource_path: str):
    """删除资源"""
    try:
        resource_service.delete_resource(resource_path)
        return {"message": "Resource deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resource not found") 