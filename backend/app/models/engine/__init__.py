"""
数据库引擎模块
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from app.core.config import settings
from app.utils.logging import em_logger


# 创建数据库引擎
DATABASE_URL = settings.get_database_url()
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


@contextmanager
def get_db():
    """获取数据库会话的上下文管理器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    # 导入所有模型以确保它们被注册到Base中
    from app.models.tools.tool_execution import ToolExecution  # noqa: F401
    # 导入MCP广场相关模型
    from app.models.modules.mcp_marketplace import (  # noqa: F401
        McpModule, McpTool, McpCategory
    )
    from app.models.modules.mcp_services import McpService  # noqa: F401
    # 导入用户和租户模型
    from app.models.modules.users import User, Tenant, UserTenant  # noqa: F401
    # 导入统计相关模型
    from app.models.statistics import (  # noqa: F401
        ServiceStatistics, ModuleStatistics,
        ToolStatistics, ServiceCallStatistics
    )
    
    # 自动同步数据库模型和表结构
    sync_db_model()
    
    # 初始化基础数据
    from app.models.engine.init_data import (
        migrate_database, init_category_data, 
        auto_categorize_modules, init_demo_modules, init_admin_users
    )
    
    # 先执行数据库迁移，确保表结构正确
    migrate_database()
    
    # 初始化分类数据
    init_category_data()
    
    # 自动对现有模块进行分类
    auto_categorize_modules()
    
    # 初始化演示模块
    init_demo_modules()
    
    # 初始化管理员用户
    init_admin_users()


def sync_db_model():
    """
    自动同步SQLAlchemy模型与数据库表结构
    - 检查模型中的字段是否存在于数据库表中，不存在则创建
    - 检查数据库表中的字段是否存在于模型中，不存在则删除
    """
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    metadata = Base.metadata
    
    em_logger.info("开始同步数据库模型与表结构...")
    
    # 获取数据库中所有已存在的表
    existing_tables = set(inspector.get_table_names())
    
    # 获取模型中定义的所有表
    model_tables = set(metadata.tables.keys())
    
    # 创建新表
    tables_to_create = model_tables - existing_tables
    if tables_to_create:
        tables_str = ", ".join(tables_to_create)
        em_logger.info(f"发现新表，准备创建: {tables_str}")
        # 仅创建新表
        for table_name in tables_to_create:
            metadata.tables[table_name].create(bind=engine)
            em_logger.info(f"创建表 {table_name} 成功")
    
    # 处理已存在的表，进行字段比对
    tables_to_sync = model_tables.intersection(existing_tables)
    for table_name in tables_to_sync:
        sync_table_columns(table_name, inspector, metadata)


def sync_table_columns(table_name, inspector, metadata):
    """同步单个表的列结构"""
    import sqlalchemy as sa
    
    # 获取表对象
    table = metadata.tables[table_name]
    
    # 获取数据库中表的当前列
    db_columns = {col['name']: col for col in inspector.get_columns(table_name)}
    db_column_names = set(db_columns.keys())
    
    # 获取模型中定义的列
    model_column_names = set(c.name for c in table.columns)
    
    # 处理需要添加的列
    columns_to_add = model_column_names - db_column_names
    if columns_to_add:
        with engine.begin() as conn:
            for col_name in columns_to_add:
                column = table.columns[col_name]
                
                # 构建列类型的SQL表达式
                type_compiler = engine.dialect.type_compiler
                column_type = type_compiler.process(column.type)
                
                # 处理默认值
                default_clause = ""
                try:
                    if (column.default is not None and 
                            not isinstance(column.default, sa.schema.Sequence)):
                        # 对于简单的常量默认值
                        if (not column.default.is_callable and 
                                not column.default.is_clause_element):
                            if isinstance(column.default.arg, str):
                                default_clause = f" DEFAULT '{column.default.arg}'"
                            elif isinstance(column.default.arg, bool):
                                default_val = 1 if column.default.arg else 0
                                default_clause = f" DEFAULT {default_val}"
                            elif column.default.arg is not None:
                                default_clause = f" DEFAULT {column.default.arg}"
                        # 对于复杂的默认值，不添加默认值子句
                except Exception as e:
                    em_logger.warning(
                        f"处理列 {col_name} 的默认值时出错: {str(e)}")
                
                # 处理可空性
                nullable_clause = "" if column.nullable else " NOT NULL"
                
                # 构建ALTER TABLE语句
                alter_stmt = (
                    f"ALTER TABLE {table_name} ADD COLUMN {col_name} "
                    f"{column_type}{nullable_clause}{default_clause}"
                )
                em_logger.info(f"添加列: {alter_stmt}")
                conn.execute(sa.text(alter_stmt))
                em_logger.info(f"表 {table_name} 添加列 {col_name} 成功")
    
    # 处理需要删除的列 (排除主键和外键)
    columns_to_drop = db_column_names - model_column_names
    if columns_to_drop:
        # 获取主键和外键约束相关的列
        primary_keys = set()
        foreign_keys = set()
        
        # 获取主键列
        pk_constraint = inspector.get_pk_constraint(table_name)
        if pk_constraint and 'constrained_columns' in pk_constraint:
            primary_keys.update(pk_constraint['constrained_columns'])
        
        # 获取外键列
        for fk in inspector.get_foreign_keys(table_name):
            if 'constrained_columns' in fk:
                foreign_keys.update(fk['constrained_columns'])
        
        # 排除主键和外键列
        protected_columns = primary_keys.union(foreign_keys)
        safe_columns_to_drop = columns_to_drop - protected_columns
        
        if protected_columns.intersection(columns_to_drop):
            skipped = protected_columns.intersection(columns_to_drop)
            em_logger.warning(
                f"跳过删除主键或外键列: {', '.join(skipped)}")
        
        # 安全删除非主键、非外键的列
        with engine.begin() as conn:
            for col_name in safe_columns_to_drop:
                alter_stmt = f"ALTER TABLE {table_name} DROP COLUMN {col_name}"
                em_logger.info(f"删除列: {alter_stmt}")
                conn.execute(sa.text(alter_stmt))
                em_logger.info(f"表 {table_name} 删除列 {col_name} 成功")
                
    # TODO: 同步索引和约束（未来可以实现）
    # 这部分更复杂，需要比较索引和约束的差异
    # 然后添加/删除/修改相应的索引和约束

