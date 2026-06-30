"""
MCP 模板分组数据访问层。

Repository 只负责数据库查询，不承载业务校验、外部接口调用或响应封装。
事务和 Session 生命周期由 Service 层控制。
"""
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.group.group import McpGroup


class McpTemplateGroupRepository:
    """MCP 模板分组 Repository。"""

    @staticmethod
    def get_templates_count(db: Session, group_id: int) -> int:
        """查询某分组下的模板数量。"""
        sql = text("SELECT COUNT(*) FROM mcp_templates WHERE category_id = :id")
        result = db.execute(sql.bindparams(id=group_id))
        return result.scalar() or 0

    @staticmethod
    def get_group_stat(db: Session, group_id: int) -> dict:
        """获取单个分组的完整统计信息。

        返回:
            dict: 包含 templates_count, services_count, call_count 的统计信息
        """
        # 1. 查询该分组下的模板数量
        modules_count_sql = text(
            "SELECT COUNT(*) FROM mcp_templates WHERE category_id = :group_id"
        )
        modules_count = db.execute(
            modules_count_sql.bindparams(group_id=group_id)
        ).scalar() or 0

        # 2. 查询该分组下模板发布的服务数量
        services_count_sql = text("""
            SELECT COUNT(DISTINCT s.id)
            FROM published_services s
            INNER JOIN mcp_templates m ON s.module_id = m.id
            WHERE m.category_id = :group_id
        """)
        services_count = db.execute(
            services_count_sql.bindparams(group_id=group_id)
        ).scalar() or 0

        # 3. 查询该分组下服务的总调用次数
        call_count_sql = text("""
            SELECT COUNT(t.id)
            FROM tool_executions t
            INNER JOIN mcp_templates m ON t.module_id = m.id
            WHERE m.category_id = :group_id
        """)
        call_count = db.execute(
            call_count_sql.bindparams(group_id=group_id)
        ).scalar() or 0

        return {
            "templates_count": modules_count,
            "services_count": services_count,
            "call_count": call_count
        }

    @staticmethod
    def get_top_groups_by_stat(
        db: Session,
        order_by: str = "templates_count",
        limit: int = 10,
        desc: bool = True,
    ) -> list:
        """获取按统计指标排序的分组列表。

        参数:
            order_by: 排序字段，可选值: templates_count, services_count, call_count
            limit: 返回数量限制
            desc: 是否降序排列

        返回:
            list: 排序后的分组统计列表
        """
        valid_fields = ["templates_count", "services_count", "call_count"]
        if order_by not in valid_fields:
            order_by = "templates_count"

        direction = "DESC" if desc else "ASC"

        if order_by == "templates_count":
            query = f"""
                SELECT g.id, g.name, COUNT(m.id) as stat_value
                FROM mcp_template_groups g
                LEFT JOIN mcp_templates m ON g.id = m.category_id
                GROUP BY g.id, g.name
                ORDER BY stat_value {direction}
                LIMIT :limit
            """
        elif order_by == "services_count":
            query = f"""
                SELECT g.id, g.name, COUNT(DISTINCT s.id) as stat_value
                FROM mcp_template_groups g
                LEFT JOIN mcp_templates m ON g.id = m.category_id
                LEFT JOIN published_services s ON m.id = s.module_id
                GROUP BY g.id, g.name
                ORDER BY stat_value {direction}
                LIMIT :limit
            """
        else:  # call_count
            query = f"""
                SELECT g.id, g.name, COUNT(t.id) as stat_value
                FROM mcp_template_groups g
                LEFT JOIN mcp_templates m ON g.id = m.category_id
                LEFT JOIN tool_executions t ON m.id = t.module_id
                GROUP BY g.id, g.name
                ORDER BY stat_value {direction}
                LIMIT :limit
            """

        results = db.execute(text(query).bindparams(limit=limit)).fetchall()

        group_stats = []
        repo = McpTemplateGroupRepository
        for row in results:
            group_id, group_name, stat_value = row
            group = db.get(McpGroup, group_id)
            if group:
                stat = repo.get_group_stat(db, group_id)
                stat_dict = {
                    "group_id": group_id,
                    "group_name": group_name,
                    "templates_count": stat["templates_count"],
                    "services_count": stat["services_count"],
                    "call_count": stat["call_count"],
                    "rank_value": stat_value,
                    "rank_field": order_by,
                }
                group_stats.append(stat_dict)

        return group_stats
