"""迁移脚本：将早期分类表改名为模板分组表。"""
from app.utils.logging import mcp_logger
from app.models.engine.migrations._helpers import rename_table_if_needed


def run(db):
    """执行迁移：将 mcp_categories 表改名为 mcp_group。"""
    try:
        renamed = rename_table_if_needed(db, "mcp_categories", "mcp_group")
        if renamed:
            mcp_logger.info("检测到 mcp_categories 表，开始重命名为 mcp_group")
            db.commit()
            mcp_logger.info("表重命名成功：mcp_categories -> mcp_group")
        else:
            mcp_logger.info("未检测到 mcp_categories 表，无需执行迁移")

    except Exception as e:
        db.rollback()
        mcp_logger.error(f"迁移失败：{str(e)}")
        raise
