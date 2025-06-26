"""
分组相关模型
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime
)
from sqlalchemy.sql import text

from app.models.engine import Base, get_db
from app.core.utils import now_beijing


class McpGroup(Base):
    """MCP分组信息模型"""
    __tablename__ = "mcp_group"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True)  # 分组名称
    description = Column(Text, nullable=True)  # 分组描述
    icon = Column(String(200), nullable=True)  # 分组图标
    order = Column(Integer, default=0)  # 排序序号
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    user_id = Column(Integer, nullable=True, index=True)  # 创建者ID

    def to_dict(self, include_modules_count=True):
        """转换为字典格式"""
        modules_count = 0
        if include_modules_count:
            # 获取模块数量通过直接查询
            with get_db() as db:
                # 使用原生SQL查询避免循环导入
                sql = text("SELECT COUNT(*) FROM mcp_modules WHERE category_id = :id")
                result = sql.bindparams(id=self.id)
                modules_count = db.execute(result).scalar()

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "order": self.order,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "modules_count": modules_count,
            "user_id": self.user_id
        }

    def to_stat_dict(self):
        """获取分组统计信息
        
        返回:
            dict: 包含模板数量、服务数量、调用次数的统计信息
        """
        with get_db() as db:
            # 1. 查询该分组下的模板数量
            modules_count_query = """
                SELECT COUNT(*) FROM mcp_modules 
                WHERE category_id = :group_id
            """
            modules_count = db.execute(
                text(modules_count_query).bindparams(group_id=self.id)
            ).scalar() or 0

            # 2. 查询该分组下模板发布的服务数量
            services_count_query = """
                SELECT COUNT(DISTINCT s.id) 
                FROM mcp_services s
                INNER JOIN mcp_modules m ON s.module_id = m.id
                WHERE m.category_id = :group_id
            """
            services_count = db.execute(
                text(services_count_query).bindparams(group_id=self.id)
            ).scalar() or 0

            # 3. 查询该分组下服务的总调用次数
            call_count_query = """
                SELECT COUNT(t.id)
                FROM tool_executions t
                INNER JOIN mcp_modules m ON t.module_id = m.id
                WHERE m.category_id = :group_id
            """
            call_count = db.execute(
                text(call_count_query).bindparams(group_id=self.id)
            ).scalar() or 0

            return {
                "group_id": self.id,
                "group_name": self.name,
                "templates_count": modules_count,
                "services_count": services_count,
                "call_count": call_count
            }

    @classmethod
    def get_top_groups_by_stat(cls, order_by="templates_count", limit=10, desc=True):
        """获取按统计指标排序的分组列表
        
        参数:
            order_by: 排序字段，可选值: templates_count, services_count, call_count
            limit: 返回数量限制
            desc: 是否降序排列
            
        返回:
            list: 排序后的分组统计列表
        """
        with get_db() as db:
            # 验证排序字段
            valid_fields = ["templates_count", "services_count", "call_count"]
            if order_by not in valid_fields:
                order_by = "templates_count"
            
            # 构建不同的SQL查询
            if order_by == "templates_count":
                # 按模板数量排序
                query = """
                    SELECT 
                        g.id,
                        g.name,
                        COUNT(m.id) as stat_value
                    FROM mcp_group g
                    LEFT JOIN mcp_modules m ON g.id = m.category_id
                    GROUP BY g.id, g.name
                    ORDER BY stat_value {order}
                    LIMIT :limit
                """.format(order="DESC" if desc else "ASC")
                
            elif order_by == "services_count":
                # 按服务数量排序
                query = """
                    SELECT 
                        g.id,
                        g.name,
                        COUNT(DISTINCT s.id) as stat_value
                    FROM mcp_group g
                    LEFT JOIN mcp_modules m ON g.id = m.category_id
                    LEFT JOIN mcp_services s ON m.id = s.module_id
                    GROUP BY g.id, g.name
                    ORDER BY stat_value {order}
                    LIMIT :limit
                """.format(order="DESC" if desc else "ASC")
                
            else:  # call_count
                # 按调用次数排序
                query = """
                    SELECT 
                        g.id,
                        g.name,
                        COUNT(t.id) as stat_value
                    FROM mcp_group g
                    LEFT JOIN mcp_modules m ON g.id = m.category_id
                    LEFT JOIN tool_executions t ON m.id = t.module_id
                    GROUP BY g.id, g.name
                    ORDER BY stat_value {order}
                    LIMIT :limit
                """.format(order="DESC" if desc else "ASC")
            
            # 执行查询
            results = db.execute(text(query).bindparams(limit=limit)).fetchall()
            
            # 为每个分组获取完整统计信息
            group_stats = []
            for row in results:
                group_id, group_name, stat_value = row
                group = db.get(cls, group_id)
                if group:
                    stat_dict = group.to_stat_dict()
                    stat_dict["rank_value"] = stat_value
                    stat_dict["rank_field"] = order_by
                    stat_dict["group_name"] = group_name
                    group_stats.append(stat_dict)
            
            return group_stats

    @classmethod
    def get_module_stats_ranking(cls, order_by="services_count", limit=10, desc=True):
        """获取模板按统计指标排序的列表
        
        参数:
            order_by: 排序字段，可选值: services_count, call_count
            limit: 返回数量限制
            desc: 是否降序排列
            
        返回:
            list: 排序后的模板统计列表
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
                        COUNT(DISTINCT s.id) as stat_value
                    FROM mcp_modules m
                    LEFT JOIN mcp_services s ON m.id = s.module_id
                    GROUP BY m.id, m.name
                    ORDER BY stat_value {order}
                    LIMIT :limit
                """.format(order="DESC" if desc else "ASC")
                
            else:  # call_count
                # 按调用次数排序
                query = """
                    SELECT 
                        m.id,
                        m.name,
                        COUNT(t.id) as stat_value
                    FROM mcp_modules m
                    LEFT JOIN tool_executions t ON m.id = t.module_id
                    GROUP BY m.id, m.name
                    ORDER BY stat_value {order}
                    LIMIT :limit
                """.format(order="DESC" if desc else "ASC")
            
            # 执行查询
            results = db.execute(text(query).bindparams(limit=limit)).fetchall()
            
            # 为每个模板获取完整统计信息
            module_stats = []
            for row in results:
                module_id, module_name, stat_value = row
                # 创建一个简化的模块统计信息
                module_stats.append({
                    "module_id": module_id,
                    "module_name": module_name,
                    "rank_value": stat_value,
                    "rank_field": order_by
                })
            
            return module_stats
