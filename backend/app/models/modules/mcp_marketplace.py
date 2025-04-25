"""
MCP广场相关模型
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime
)
import json
from sqlalchemy.sql import text

from app.models.engine import Base, get_db
from app.core.utils import now_beijing


class McpCategory(Base):
    """MCP分组信息模型"""
    __tablename__ = "mcp_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True)  # 分组名称
    description = Column(Text, nullable=True)  # 分组描述
    icon = Column(String(200), nullable=True)  # 分组图标
    order = Column(Integer, default=0)  # 排序序号
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    
    def to_dict(self):
        """转换为字典格式"""
        # 获取模块数量通过直接查询
        with get_db() as db:
            # 使用原生SQL查询避免循环导入
            query = "SELECT COUNT(*) FROM mcp_modules WHERE category_id = :id"
            sql = text(query).bindparams(id=self.id)
            modules_count = db.execute(sql).scalar()
            
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "order": self.order,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "modules_count": modules_count
        }


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
    category_id = Column(Integer, nullable=True, index=True)  # 分组ID
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    code = Column(Text)  # 模块代码
    config_schema = Column(Text)  # 配置项模式，用于存储key, secret等字段的配置模式，JSON格式
    markdown_docs = Column(Text)  # 模块的Markdown格式文档内容
    creator_id = Column(Integer, nullable=True, index=True)  # 创建者ID
    is_public = Column(Boolean, default=True)  # 是否公开，True为公开，False为私有

    def to_dict(self):
        """转换为字典格式"""
        # 获取分类名称和工具数量通过直接查询
        category_name = None
        tools_count = 0
        creator_name = None
        
        with get_db() as db:
            # 获取分类名称
            if self.category_id:
                query = "SELECT name FROM mcp_categories WHERE id = :id"
                sql = text(query).bindparams(id=self.category_id)
                result = db.execute(sql).first()
                category_name = result[0] if result else None
            
            # 获取工具数量
            query = "SELECT COUNT(*) FROM mcp_tools WHERE module_id = :id"
            sql = text(query).bindparams(id=self.id)
            tools_count = db.execute(sql).scalar()
            
            # 获取创建者名称
            if self.creator_id:
                query = "SELECT username FROM users WHERE id = :id"
                sql = text(query).bindparams(id=self.creator_id)
                result = db.execute(sql).first()
                creator_name = result[0] if result else None
                
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
            "category_name": category_name,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "tools_count": tools_count,
            "code": self.code,
            "config_schema": config_dict,
            "markdown_docs": self.markdown_docs,
            "creator_id": self.creator_id,
            "creator_name": creator_name,
            "is_public": self.is_public
        }


class McpTool(Base):
    """MCP工具信息模型"""
    __tablename__ = "mcp_tools"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, index=True)  # 移除外键约束
    name = Column(String(100), index=True)  # 工具名称
    function_name = Column(String(100))  # 对应的函数名
    description = Column(Text)  # 工具描述
    parameters = Column(Text)  # 参数定义，JSON格式
    sample_usage = Column(Text)  # 使用示例
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    is_enabled = Column(Boolean, default=True)  # 是否已启用

    def to_dict(self):
        """转换为字典格式"""
        params = json.loads(self.parameters) if self.parameters else {}
        
        # 获取模块名称通过直接查询
        module_name = None
        with get_db() as db:
            from app.models.modules.mcp_marketplace import McpModule
            module = db.query(McpModule).filter(
                McpModule.id == self.module_id
            ).first()
            if module:
                module_name = module.name
        
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
            "module_name": module_name
        } 