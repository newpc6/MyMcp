"""
迁移脚本：重命名McpModule表中的creator_id字段为user_id，并为McpService表添加user_id字段

此迁移进行以下操作：
1. 修改mcp_modules表，将creator_id字段重命名为user_id
2. 添加user_id字段到mcp_services表，表示服务创建者
"""
from sqlalchemy import text
from app.utils.logging import em_logger


def run(db):
    """执行迁移"""
    try:
        # 1. 在mcp_modules表中添加user_id字段并复制creator_id的值
        em_logger.info("开始迁移: 重命名creator_id为user_id并为服务添加user_id")
        
        # 检查mcp_modules表结构
        modules_columns_query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'mcp_modules'
        """
        result = db.execute(text(modules_columns_query)).fetchall()
        modules_column_names = [row[0] for row in result]
        
        # 如果表中有creator_id但没有user_id，则进行重命名迁移
        if 'creator_id' in modules_column_names and 'user_id' not in modules_column_names:
            em_logger.info("重命名mcp_modules表中的creator_id为user_id")
            
            # MySQL支持直接重命名列
            db.execute(text("""
                ALTER TABLE mcp_modules
                CHANGE COLUMN creator_id user_id INTEGER
            """))
            
            # 确保索引存在
            # 先检查索引是否存在
            index_query = """
                SELECT INDEX_NAME 
                FROM INFORMATION_SCHEMA.STATISTICS 
                WHERE TABLE_NAME = 'mcp_modules' 
                AND INDEX_NAME = 'ix_mcp_modules_user_id'
            """
            indexes = db.execute(text(index_query)).fetchall()
            
            if not indexes:
                db.execute(text("""
                    CREATE INDEX ix_mcp_modules_user_id ON mcp_modules (user_id)
                """))
            
            em_logger.info("成功重命名mcp_modules表中的creator_id为user_id")
        else:
            if 'user_id' in modules_column_names:
                em_logger.info("mcp_modules表中已有user_id字段，跳过重命名")
            else:
                # 如果表中既没有creator_id又没有user_id，则直接添加user_id
                em_logger.info("mcp_modules表中添加user_id字段")
                db.execute(text("""
                    ALTER TABLE mcp_modules
                    ADD COLUMN user_id INTEGER
                """))
                # 创建索引
                db.execute(text("""
                    CREATE INDEX ix_mcp_modules_user_id ON mcp_modules (user_id)
                """))
        
        # 2. 为mcp_services表添加user_id字段
        # 检查mcp_services表结构
        services_columns_query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'mcp_services'
        """
        result = db.execute(text(services_columns_query)).fetchall()
        services_column_names = [row[0] for row in result]
        
        if 'user_id' not in services_column_names:
            em_logger.info("为mcp_services表添加user_id字段")
            db.execute(text("""
                ALTER TABLE mcp_services
                ADD COLUMN user_id INTEGER
            """))
            
            # 创建索引
            db.execute(text("""
                CREATE INDEX ix_mcp_services_user_id ON mcp_services (user_id)
            """))
            
            # 根据模块创建者更新服务的user_id
            em_logger.info("更新mcp_services表中的user_id")
            db.execute(text("""
                UPDATE mcp_services
                SET user_id = (
                    SELECT user_id FROM mcp_modules
                    WHERE mcp_modules.id = mcp_services.module_id
                )
                WHERE EXISTS (
                    SELECT 1 FROM mcp_modules
                    WHERE mcp_modules.id = mcp_services.module_id
                    AND mcp_modules.user_id IS NOT NULL
                )
            """))
            
            em_logger.info("成功为mcp_services表添加并更新user_id字段")
        else:
            em_logger.info("mcp_services表中已有user_id字段，跳过添加")
        
        db.commit()
        em_logger.info("成功完成迁移: 重命名creator_id为user_id并为服务添加user_id")
        return True
    except Exception as e:
        db.rollback()
        em_logger.error(f"迁移失败: {str(e)}")
        return False 