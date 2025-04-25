"""
迁移脚本：为McpModule表添加创建者和可见性字段

此迁移添加以下字段：
1. user_id: 创建者ID，关联到users表
2. is_public: 是否公开，默认为True
"""
from sqlalchemy import text
from app.utils.logging import em_logger


def run(db):
    """执行迁移"""
    try:
        # 检查字段是否已存在
        columns_query = "PRAGMA table_info(mcp_modules)"
        columns = db.execute(text(columns_query)).fetchall()
        column_names = [col[1] for col in columns]  # 第二个元素是列名
        
        # 检查并添加user_id字段
        if 'user_id' not in column_names:
            em_logger.info("添加user_id字段到mcp_modules表")
            db.execute(text("""
                ALTER TABLE mcp_modules
                ADD COLUMN user_id INTEGER
            """))
            # 创建索引
            db.execute(text("""
                CREATE INDEX ix_mcp_modules_user_id ON mcp_modules (user_id)
            """))
        else:
            em_logger.info("user_id字段已存在，跳过")
        
        # 检查并添加is_public字段
        if 'is_public' not in column_names:
            em_logger.info("添加is_public字段到mcp_modules表")
            db.execute(text("""
                ALTER TABLE mcp_modules
                ADD COLUMN is_public BOOLEAN DEFAULT 1
            """))
        else:
            em_logger.info("is_public字段已存在，跳过")
        
        db.commit()
        em_logger.info("成功完成迁移: 添加user_id和is_public字段")
        return True
    except Exception as e:
        db.rollback()
        em_logger.error(f"迁移失败: {str(e)}")
        return False 