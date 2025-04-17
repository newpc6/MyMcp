from pydantic import BaseModel
from typing import Dict, Any, Optional


class MCPToolInfo(BaseModel):
    """MCP工具信息模型"""
    name: str
    doc: str
    parameters: Dict[str, Dict[str, Any]]
    return_type: str


class ToolInfo(BaseModel):
    """工具信息模型"""
    name: str
    doc: str
    parameters: Dict[str, Dict[str, Any]]
    return_type: str
    module: str
    file_path: str


class ToolContent(BaseModel):
    """工具内容模型"""
    content: str


class ToolCreate(BaseModel):
    """工具创建模型"""
    path: str
    content: str


class ToolUpdate(BaseModel):
    """工具更新模型"""
    content: str


class ToolCall(BaseModel):
    """工具调用模型"""
    tool_name: str
    parameters: Dict[str, Any] 