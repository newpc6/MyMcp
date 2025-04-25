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
        modules_columns_query = "PRAGMA table_info(mcp_modules)"
        modules_columns = db.execute(text(modules_columns_query)).fetchall()
        modules_column_names = [col[1] for col in modules_columns]
        
        # 如果表中有creator_id但没有user_id，则进行重命名迁移
        if 'creator_id' in modules_column_names and 'user_id' not in modules_column_names:
            em_logger.info("重命名mcp_modules表中的creator_id为user_id")
            
            # SQLite不直接支持重命名列，需要通过多步操作实现
            # 1. 创建临时表
            db.execute(text("""
                CREATE TABLE mcp_modules_temp (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    module_path TEXT NOT NULL,
                    author TEXT,
                    version TEXT,
                    tags TEXT,
                    icon TEXT,
                    is_hosted BOOLEAN,
                    repository_url TEXT,
                    category_id INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    code TEXT,
                    config_schema TEXT,
                    markdown_docs TEXT,
                    user_id INTEGER,
                    is_public BOOLEAN DEFAULT 1
                )
            """))
            
            # 2. 复制数据，将creator_id的值复制到user_id
            db.execute(text("""
                INSERT INTO mcp_modules_temp 
                SELECT 
                    id, name, description, module_path, author, version, 
                    tags, icon, is_hosted, repository_url, category_id, 
                    created_at, updated_at, code, config_schema, markdown_docs, 
                    creator_id, is_public
                FROM mcp_modules
            """))
            
            # 3. 删除旧表
            db.execute(text("DROP TABLE mcp_modules"))
            
            # 4. 重命名新表
            db.execute(text("ALTER TABLE mcp_modules_temp RENAME TO mcp_modules"))
            
            # 5. 创建索引
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
        services_columns_query = "PRAGMA table_info(mcp_services)"
        services_columns = db.execute(text(services_columns_query)).fetchall()
        services_column_names = [col[1] for col in services_columns]
        
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