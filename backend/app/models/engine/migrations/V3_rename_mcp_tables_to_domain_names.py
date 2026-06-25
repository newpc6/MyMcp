"""迁移脚本：将历史 MCP 表名改为业务语义表名。"""
from app.models.engine.migrations._helpers import rename_table_if_needed
from app.utils.logging import mcp_logger


TABLE_RENAMES = (
    ("mcp_group", "mcp_template_groups"),
    ("mcp_modules", "mcp_templates"),
    ("mcp_tools", "mcp_template_tools"),
    ("mcp_services", "published_services"),
    ("mcp_service_secrets", "published_service_secrets"),
    ("mcp_secret_statistics", "published_service_secret_statistics"),
    ("mcp_access_logs", "published_service_access_logs"),
)


def run(db):
    """执行表名重命名；已迁移或不存在时跳过。"""
    try:
        renamed_tables = []
        for old_name, new_name in TABLE_RENAMES:
            if rename_table_if_needed(db, old_name, new_name):
                renamed_tables.append(f"{old_name} -> {new_name}")

        db.commit()

        if renamed_tables:
            mcp_logger.info("表名迁移完成: " + ", ".join(renamed_tables))
        else:
            mcp_logger.info("表名已是最新，无需迁移")
    except Exception as e:
        db.rollback()
        mcp_logger.error(f"表名迁移失败：{str(e)}")
        raise
