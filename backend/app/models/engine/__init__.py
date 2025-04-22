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

# 创建数据库文件路径
database_path = os.path.join(settings.MCP_BASE_DIR, settings.DATABASE_FILE)
engine = create_engine(
    f"sqlite:///{database_path}",
    connect_args={"check_same_thread": False}
)

# 创建Session工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    from app.models.activities.activity import Activity  # noqa: F401
    # 导入MCP广场相关模型
    from app.models.modules.mcp_marketplace import (  # noqa: F401
        McpModule, McpTool
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine) 