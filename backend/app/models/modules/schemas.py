from pydantic import BaseModel
from typing import Dict, Any


class ModuleInfo(BaseModel):
    """模块信息模型"""
    path: str
    content: str
    size: int


class ModuleContent(BaseModel):
    """模块内容模型"""
    content: str


class ModuleCreate(BaseModel):
    """模块创建模型"""
    path: str
    content: str


class ModuleUpdate(BaseModel):
    """模块更新模型"""
    content: str


class ModuleEdit(BaseModel):
    """模块编辑模型"""
    content: str


class FileContent(BaseModel):
    """文件内容模型"""
    content: str 