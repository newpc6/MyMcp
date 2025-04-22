"""
添加代码相关字段迁移

向mcp_modules表添加code和config_schema字段，用于存储模块代码和配置模式
"""
from sqlalchemy import text
from app.utils.logging import em_logger


def run(db):
    """执行迁移"""
    try:
        # 检查mcp_modules表中字段
        check_column_sql = text(
            "PRAGMA table_info(mcp_modules)"
        )
        columns = db.execute(check_column_sql).fetchall()
        column_names = [col[1] for col in columns]  # 字段名在结果的第2列
        
        # 检查并添加code字段
        if 'code' not in column_names:
            em_logger.info("向mcp_modules表添加code字段")
            db.execute(text(
                "ALTER TABLE mcp_modules "
                "ADD COLUMN code TEXT"
            ))
            em_logger.info("code字段添加完成")
        else:
            em_logger.info("code字段已存在")
            
        # 检查并添加config_schema字段
        if 'config_schema' not in column_names:
            em_logger.info("向mcp_modules表添加config_schema字段")
            db.execute(text(
                "ALTER TABLE mcp_modules "
                "ADD COLUMN config_schema TEXT"
            ))
            em_logger.info("config_schema字段添加完成")
        else:
            em_logger.info("config_schema字段已存在")
            
        db.commit()
    except Exception as e:
        db.rollback()
        em_logger.error(f"添加代码相关字段迁移失败: {str(e)}")
        raise 