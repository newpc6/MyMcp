"""
MCP广场相关模型
"""
from typing import Dict
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime
)
from app.models.engine import Base
from app.core.utils import now_beijing
import json

from app.models.group.group import McpGroup


class McpModule(Base):
    """MCP模块信息模型"""
    __tablename__ = "mcp_templates"
    __table_args__ = {'extend_existing': True}
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
    category_id = Column(Integer, nullable=True, index=True)  # 分组ID
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    code = Column(Text)  # 模块代码
    config_schema = Column(Text)  # 配置项模式，用于存储key, secret等字段的配置模式，JSON格式
    markdown_docs = Column(Text)  # 模块的Markdown格式文档内容
    user_id = Column(Integer, nullable=True, index=True)  # 创建者ID
    is_public = Column(Boolean, default=True)  # 是否公开，True为公开，False为私有

    def to_dict(self, mcp_template_groups: Dict[int, 'McpGroup'] = None):
        """转换为字典格式"""

        config_dict = {}
        if self.config_schema:
            try:
                config_dict = json.loads(self.config_schema)
            except json.JSONDecodeError:
                pass

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
            "category_id": self.category_id,
            "category_name": (
                mcp_template_groups.get(self.category_id).name
                if mcp_template_groups and self.category_id else None
            ),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "code": self.code,
            "config_schema": config_dict,
            "markdown_docs": self.markdown_docs,
            "user_id": self.user_id,
            "is_public": self.is_public
        }
