from pydantic import BaseModel
from typing import Optional, Literal


class ProtocolInfo(BaseModel):
    """MCP协议文件信息"""
    path: str
    name: str
    description: str
    lastModified: str


class ProtocolContent(BaseModel):
    """MCP协议文件内容"""
    content: str


class ProtocolCreate(BaseModel):
    """创建MCP协议请求"""
    path: str
    content: str


class ProtocolUpdate(BaseModel):
    """更新MCP协议请求"""
    content: str


class McpServiceInfo(BaseModel):
    """MCP服务状态信息"""
    status: Literal["running", "stopped", "error"]
    uptime: str
    version: str
    connectionCount: int


class McpServiceAction(BaseModel):
    """MCP服务控制操作"""
    action: Literal["start", "stop", "restart"]


class McpServiceActionResult(BaseModel):
    """MCP服务控制操作结果"""
    success: bool
    message: str 