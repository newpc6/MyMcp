"""
初始表结构迁移

创建第一版的表结构，包括mcp_categories表
"""
from sqlalchemy import text
from app.utils.logging import em_logger


def run(db):
    """执行迁移"""
    try:
        # 检查mcp_categories表是否存在
        check_categories_sql = text(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='mcp_categories'"
        )
        result = db.execute(check_categories_sql).fetchone()
        if not result:
            # 创建分类表
            em_logger.info("创建mcp_categories表")
            db.execute(text("""
                CREATE TABLE mcp_categories (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    icon VARCHAR(200),
                    order INTEGER DEFAULT 0,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            db.commit()
            em_logger.info("mcp_categories表创建完成")
        else:
            em_logger.info("mcp_categories表已存在")
    except Exception as e:
        db.rollback()
        em_logger.error(f"初始表结构迁移失败: {str(e)}")
        raise 