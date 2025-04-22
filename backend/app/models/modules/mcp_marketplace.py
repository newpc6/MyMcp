"""
MCP广场相关模型
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
import json

from app.models.engine import Base
from app.core.utils import now_beijing


class McpModule(Base):
    """MCP模块信息模型"""
    __tablename__ = "mcp_modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True)  # 模块名称
    description = Column(Text)  # 模块描述
    # 模块路径，如repository.tavily_tool
    module_path = Column(String(200), index=True)
    author = Column(String(100))  # 模块作者
    version = Column(String(50))  # 版本
    tags = Column(String(200))  # 标签，以逗号分隔
    icon = Column(String(200))  # 图标URL
    is_hosted = Column(Boolean, default=False)  # 是否为托管模块
    repository_url = Column(String(200))  # 代码仓库地址
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    
    # 关联该模块下的工具
    tools = relationship(
        "McpTool", 
        back_populates="module", 
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "module_path": self.module_path,
            "author": self.author,
            "version": self.version,
            "tags": self.tags.split(",") if self.tags else [],
            "icon": self.icon,
            "is_hosted": self.is_hosted,
            "repository_url": self.repository_url,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "tools_count": len(self.tools)
        }


class McpTool(Base):
    """MCP工具信息模型"""
    __tablename__ = "mcp_tools"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("mcp_modules.id"))
    name = Column(String(100), index=True)  # 工具名称
    function_name = Column(String(100))  # 对应的函数名
    description = Column(Text)  # 工具描述
    parameters = Column(Text)  # 参数定义，JSON格式
    sample_usage = Column(Text)  # 使用示例
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    is_enabled = Column(Boolean, default=True)  # 是否已启用
    
    # 关联所属的模块
    module = relationship("McpModule", back_populates="tools")

    def to_dict(self):
        """转换为字典格式"""
        params = json.loads(self.parameters) if self.parameters else {}
        return {
            "id": self.id,
            "module_id": self.module_id,
            "name": self.name,
            "function_name": self.function_name,
            "description": self.description,
            "parameters": params,
            "sample_usage": self.sample_usage,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_enabled": self.is_enabled,
            "module_name": self.module.name if self.module else None
        } 