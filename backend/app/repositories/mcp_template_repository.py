"""
MCP 模板数据访问层。

Repository 只负责数据库查询，不承载业务校验、外部接口调用或响应封装。
事务和 Session 生命周期由 Service 层控制。
"""
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.group.group import McpGroup


class McpTemplateRepository:
    """MCP 模板 Repository。"""

    @staticmethod
    def get_module_stat(db: Session, module_id: int) -> dict:
        """获取单个模板的统计信息。

        返回:
            dict: 包含 module_id, module_name, services_count, call_count
        """
        services_count_sql = text(
            "SELECT COUNT(*) FROM published_services WHERE module_id = :module_id"
        )
        services_count = db.execute(
            services_count_sql.bindparams(module_id=module_id)
        ).scalar() or 0

        call_count_sql = text(
            "SELECT COUNT(*) FROM tool_executions WHERE module_id = :module_id"
        )
        call_count = db.execute(
            call_count_sql.bindparams(module_id=module_id)
        ).scalar() or 0

        # 获取模板名称
        name_sql = text(
            "SELECT name FROM mcp_templates WHERE id = :module_id"
        )
        module_name = db.execute(
            name_sql.bindparams(module_id=module_id)
        ).scalar() or ""

        return {
            "module_id": module_id,
            "module_name": module_name,
            "services_count": services_count,
            "call_count": call_count
        }

    @staticmethod
    def get_module_stats_ranking(
        db: Session,
        order_by: str = "services_count",
        limit: int = 10,
        desc: bool = True,
    ) -> list:
        """获取模板按统计指标排序的排行榜。

        参数:
            order_by: 排序字段，可选值: services_count, call_count
            limit: 返回数量限制
            desc: 是否降序排列

        返回:
            list: 排序后的模板统计列表，每项包含 rank, module_id,
                  module_name, description, author, version, icon,
                  category_id, category_name, services_count, call_count,
                  rank_field, rank_value
        """
        valid_fields = ["services_count", "call_count"]
        if order_by not in valid_fields:
            order_by = "services_count"

        direction = "DESC" if desc else "ASC"

        if order_by == "services_count":
            query = f"""
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
                FROM mcp_templates m
                LEFT JOIN published_services s ON m.id = s.module_id
                LEFT JOIN tool_executions t ON m.id = t.module_id
                GROUP BY m.id, m.name, m.description, m.author,
                         m.version, m.icon, m.category_id
                ORDER BY services_count {direction}
                LIMIT :limit
            """
        else:  # call_count
            query = f"""
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
                FROM mcp_templates m
                LEFT JOIN published_services s ON m.id = s.module_id
                LEFT JOIN tool_executions t ON m.id = t.module_id
                GROUP BY m.id, m.name, m.description, m.author,
                         m.version, m.icon, m.category_id
                ORDER BY call_count {direction}
                LIMIT :limit
            """

        results = db.execute(
            text(query).bindparams(limit=limit)
        ).fetchall()

        # 获取分组名称
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
