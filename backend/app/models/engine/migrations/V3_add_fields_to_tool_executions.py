"""
迁移脚本：为工具执行记录表添加字段

此迁移添加以下字段：
1. service_id: 服务ID，关联到 McpService 表的 id
2. module_id: 模块ID，关联到 McpModule 表的 id
"""
from sqlalchemy import text
from app.utils.logging import em_logger


def run(db):
    """执行迁移"""
    try:
        # 检查字段是否已存在
        columns_query = "PRAGMA table_info(tool_executions)"
        columns = db.execute(text(columns_query)).fetchall()
        column_names = [col[1] for col in columns]  # 第二个元素是列名
        
        # 检查并添加 service_id 字段
        if 'service_id' not in column_names:
            em_logger.info("添加 service_id 字段到 tool_executions 表")
            db.execute(text("""
                ALTER TABLE tool_executions
                ADD COLUMN service_id VARCHAR(100)
            """))
            # 创建索引
            db.execute(text("""
                CREATE INDEX ix_tool_executions_service_id 
                ON tool_executions (service_id)
            """))
        else:
            em_logger.info("service_id 字段已存在，跳过")
        
        # 检查并添加 module_id 字段
        if 'module_id' not in column_names:
            em_logger.info("添加 module_id 字段到 tool_executions 表")
            db.execute(text("""
                ALTER TABLE tool_executions
                ADD COLUMN module_id INTEGER
            """))
            # 创建索引
            db.execute(text("""
                CREATE INDEX ix_tool_executions_module_id 
                ON tool_executions (module_id)
            """))
        else:
            em_logger.info("module_id 字段已存在，跳过")
        
        db.commit()
        em_logger.info("成功完成迁移: 添加 service_id 和 module_id 字段")
        return True
    except Exception as e:
        db.rollback()
        em_logger.error(f"迁移失败: {str(e)}")
        return False
