"""迁移脚本：兼容历史发布服务表结构。"""
from sqlalchemy import text

from app.models.engine.migrations._helpers import get_column, table_exists
from app.utils.logging import mcp_logger


def run(db):
    """执行迁移：将历史发布服务表的 module_id 字段调整为可空。"""
    try:
        table_name = None
        if table_exists(db, "mcp_services"):
            table_name = "mcp_services"
        elif table_exists(db, "published_services"):
            table_name = "published_services"

        if not table_name:
            mcp_logger.info("发布服务表不存在，跳过迁移")
            return

        module_id_column = get_column(db, table_name, "module_id")
        if not module_id_column:
            mcp_logger.info(f"{table_name}.module_id 不存在，跳过修改")
            return

        if module_id_column.get("nullable") is False:
            dialect_name = db.get_bind().dialect.name
            if dialect_name == "mysql":
                mcp_logger.info(f"修改 {table_name}.module_id 字段为可空")
                table_sql_name = f"`{table_name}`"
                modify_module_id_sql = text(
                    f"ALTER TABLE {table_sql_name} MODIFY COLUMN module_id "
                    "INT NULL COMMENT '模块ID，第三方服务时为空'"
                )
                db.execute(modify_module_id_sql)
            else:
                mcp_logger.warning(
                    f"{dialect_name} 不支持安全 MODIFY COLUMN，跳过 "
                    f"{table_name}.module_id 可空性调整"
                )
        else:
            mcp_logger.info(f"{table_name}.module_id 字段已为可空，跳过修改")

        db.commit()
        mcp_logger.info(f"{table_name} 表字段迁移完成")

    except Exception as e:
        db.rollback()
        mcp_logger.error(f"迁移失败：{str(e)}")
        raise
