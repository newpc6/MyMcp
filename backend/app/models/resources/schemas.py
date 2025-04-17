from pydantic import BaseModel
from typing import Dict, Any


class MCPResourceInfo(BaseModel):
    """MCP资源信息模型"""
    path: str
    doc: str
    return_type: str


class ResourceInfo(BaseModel):
    """资源信息模型"""
    path: str
    doc: str
    return_type: str
    module: str
    file_path: str


class ResourceContent(BaseModel):
    """资源内容模型"""
    content: str


class ResourceCreate(BaseModel):
    """资源创建模型"""
    path: str
    content: str


class ResourceUpdate(BaseModel):
    """资源更新模型"""
    content: str 