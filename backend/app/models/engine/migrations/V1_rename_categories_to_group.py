"""
迁移脚本：将 mcp_categories 表改名为 mcp_group
"""
from sqlalchemy import text
from app.utils.logging import mcp_logger


def run(db):
    """执行迁移：将 mcp_categories 表改名为 mcp_group"""
    try:
        # 检查 mcp_categories 表是否存在
        check_sql = text(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'mcp_categories')"
        )
        result = db.execute(check_sql).scalar()
        
        if result:
            # 表存在，执行重命名
            mcp_logger.info("检测到 mcp_categories 表，开始重命名为 mcp_group")
            
            # 重命名表
            rename_sql = text("ALTER TABLE mcp_categories RENAME TO mcp_group")
            db.execute(rename_sql)
            
            # 提交事务
            db.commit()
            
            mcp_logger.info("表重命名成功：mcp_categories -> mcp_group")
        else:
            mcp_logger.info("未检测到 mcp_categories 表，无需执行迁移")
            
    except Exception as e:
        db.rollback()
        mcp_logger.error(f"迁移失败：{str(e)}")
        raise 