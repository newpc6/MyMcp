"""
添加分类ID字段迁移

向mcp_modules表添加category_id字段，用于关联分类
"""
from sqlalchemy import text
from app.utils.logging import em_logger


def run(db):
    """执行迁移"""
    try:
        # 检查mcp_modules表中是否存在category_id字段
        check_column_sql = text(
            "PRAGMA table_info(mcp_modules)"
        )
        columns = db.execute(check_column_sql).fetchall()
        column_names = [col[1] for col in columns]  # 字段名在结果的第2列
        
        if 'category_id' not in column_names:
            # 添加category_id字段
            em_logger.info("向mcp_modules表添加category_id字段")
            db.execute(text(
                "ALTER TABLE mcp_modules "
                "ADD COLUMN category_id INTEGER"
            ))
            db.commit()
            em_logger.info("category_id字段添加完成")
        else:
            em_logger.info("category_id字段已存在")
    except Exception as e:
        db.rollback()
        em_logger.error(f"添加category_id字段迁移失败: {str(e)}")
        raise 