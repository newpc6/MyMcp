"""
迁移脚本：为 mcp_services 表添加 service_type 和 description 字段
"""
from sqlalchemy import text
from app.utils.logging import mcp_logger


def run(db):
    """执行迁移：为 mcp_services 表添加 service_type 和 description 字段"""
    try:
        # 检查 mcp_services 表是否存在
        check_table_sql = text(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'mcp_services')"
        )
        table_exists = db.execute(check_table_sql).scalar()
        
        if not table_exists:
            mcp_logger.info("mcp_services 表不存在，跳过迁移")
            return
        
        
        # 修改 module_id 字段为可空（如果需要）
        check_module_id_nullable_sql = text(
            "SELECT IS_NULLABLE FROM information_schema.columns "
            "WHERE table_name = 'mcp_services' AND column_name = 'module_id'"
        )
        module_id_nullable = db.execute(check_module_id_nullable_sql).scalar()
        
        if module_id_nullable == 'NO':
            mcp_logger.info("修改 module_id 字段为可空")
            modify_module_id_sql = text(
                "ALTER TABLE mcp_services MODIFY COLUMN module_id INT NULL "
                "COMMENT '模块ID，第三方服务时为空'"
            )
            db.execute(modify_module_id_sql)
        else:
            mcp_logger.info("module_id 字段已为可空，跳过修改")
        
        # 提交事务
        db.commit()
        mcp_logger.info("mcp_services 表字段迁移完成")
            
    except Exception as e:
        db.rollback()
        mcp_logger.error(f"迁移失败：{str(e)}")
        raise 