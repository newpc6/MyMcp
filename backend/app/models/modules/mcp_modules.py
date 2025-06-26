"""
MCP广场相关模型
"""
from typing import Dict
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime
)
from sqlalchemy.sql import text
from app.models.engine import Base, get_db
from app.core.utils import now_beijing
import json

from app.models.group.group import McpGroup


class McpModule(Base):
    """MCP模块信息模型"""
    __tablename__ = "mcp_modules"
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

    def to_dict(self, mcp_groups: Dict[int, 'McpGroup'] = None):
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
                mcp_groups.get(self.category_id).name
                if mcp_groups and self.category_id else None
            ),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "code": self.code,
            "config_schema": config_dict,
            "markdown_docs": self.markdown_docs,
            "user_id": self.user_id,
            "is_public": self.is_public
        }

    def to_stat_dict(self):
        """获取模板统计信息

        返回:
            dict: 包含发布的服务数量和服务调用次数的统计信息
        """
        with get_db() as db:
            # 1. 查询该模板发布的服务数量
            services_count_query = """
                SELECT COUNT(*) 
                FROM mcp_services 
                WHERE module_id = :module_id
            """
            services_count = db.execute(
                text(services_count_query).bindparams(module_id=self.id)
            ).scalar() or 0

            # 2. 查询该模板下服务的总调用次数
            call_count_query = """
                SELECT COUNT(*) 
                FROM tool_executions 
                WHERE module_id = :module_id
            """
            call_count = db.execute(
                text(call_count_query).bindparams(module_id=self.id)
            ).scalar() or 0

            return {
                "module_id": self.id,
                "module_name": self.name,
                "services_count": services_count,
                "call_count": call_count
            }
            
    @classmethod
    def get_module_stats_ranking(cls, order_by="services_count", 
                                 limit=10, desc=True):
        """获取模块统计信息排行榜
        
        参数:
            order_by: 排序字段，可选值: services_count, call_count
            limit: 返回数量限制
            desc: 是否降序排列
            
        返回:
            list: 排序后的模块统计列表
        """
        with get_db() as db:
            # 验证排序字段
            valid_fields = ["services_count", "call_count"]
            if order_by not in valid_fields:
                order_by = "services_count"
            
            if order_by == "services_count":
                # 按服务数量排序
                query = """
                    SELECT 
                        m.id,
                        m.name,
                        m.description,
                        m.author,
                        m.version,
                        m.icon,
                        m.category_id,
                        COUNT(DISTINCT s.id) as services_count,
                        COUNT(t.id) as call_count
                    FROM mcp_modules m
                    LEFT JOIN mcp_services s ON m.id = s.module_id
                    LEFT JOIN tool_executions t ON m.id = t.module_id
                    GROUP BY m.id, m.name, m.description, m.author, 
                             m.version, m.icon, m.category_id
                    ORDER BY services_count {order}
                    LIMIT :limit
                """.format(order="DESC" if desc else "ASC")
                
            else:  # call_count
                # 按调用次数排序
                query = """
                    SELECT 
                        m.id,
                        m.name,
                        m.description,
                        m.author,
                        m.version,
                        m.icon,
                        m.category_id,
                        COUNT(DISTINCT s.id) as services_count,
                        COUNT(t.id) as call_count
                    FROM mcp_modules m
                    LEFT JOIN mcp_services s ON m.id = s.module_id
                    LEFT JOIN tool_executions t ON m.id = t.module_id
                    GROUP BY m.id, m.name, m.description, m.author, 
                             m.version, m.icon, m.category_id
                    ORDER BY call_count {order}
                    LIMIT :limit
                """.format(order="DESC" if desc else "ASC")
            
            # 执行查询
            results = db.execute(
                text(query).bindparams(limit=limit)
            ).fetchall()
            
            # 获取分组信息
            category_ids = {row[6] for row in results if row[6] is not None}
            categories = {}
            if category_ids:
                category_records = db.query(McpGroup).filter(
                    McpGroup.id.in_(category_ids)
                ).all()
                categories = {cat.id: cat.name for cat in category_records}
            
            # 构建结果列表
            module_stats = []
            for i, row in enumerate(results, 1):
                (module_id, name, description, author, version, 
                 icon, category_id, services_count, call_count) = row
                
                rank_value = (services_count if order_by == "services_count" 
                              else call_count)
                
                module_stats.append({
                    "rank": i,
                    "module_id": module_id,
                    "module_name": name,
                    "description": description,
                    "author": author,
                    "version": version,
                    "icon": icon,
                    "category_id": category_id,
                    "category_name": categories.get(category_id),
                    "services_count": services_count,
                    "call_count": call_count,
                    "rank_field": order_by,
                    "rank_value": rank_value
                })
            
            return module_stats


# 使用示例:
# 
# # 获取服务数量前10的模板排名
# top_by_services = McpModule.get_module_stats_ranking(
#     order_by="services_count", 
#     limit=10, 
#     desc=True
# )
#
# # 获取调用次数前5的模板排名  
# top_by_calls = McpModule.get_module_stats_ranking(
#     order_by="call_count",
#     limit=5,
#     desc=True
# )
#
# 返回数据格式:
# [
#     {
#         "rank": 1,
#         "module_id": 1,
#         "module_name": "模板名称",
#         "description": "模板描述", 
#         "author": "作者",
#         "version": "1.0.0",
#         "icon": "图标",
#         "category_id": 1,
#         "category_name": "分组名称",
#         "services_count": 5,
#         "call_count": 100,
#         "rank_field": "services_count",
#         "rank_value": 5
#     }
# ]
