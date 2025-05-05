"""
数据库引擎初始化模块
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from contextlib import contextmanager

from app.core.config import settings

# 创建基本模型基类
Base = declarative_base()

# 获取数据库连接URL
database_url = settings.get_database_url()

# 创建数据库引擎
connect_args = {}
if settings.DATABASE_TYPE == "sqlite":
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args
)

# 创建Session工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 全局数据库会话对象
db = SessionLocal()

def get_global_db():
    """获取全局数据库会话对象"""
    return db

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
    from app.models.statistics import (
        ServiceStatistics, ModuleStatistics,
        ToolStatistics, ServiceCallStatistics
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
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

