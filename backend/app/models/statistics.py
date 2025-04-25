"""
统计模型

用于存储和查询MCP服务和工具调用统计数据
"""

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from .engine import Base


class ServiceStatistics(Base):
    """MCP服务统计数据"""
    
    __tablename__ = "service_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    total_services = Column(Integer, default=0)
    running_services = Column(Integer, default=0)
    stopped_services = Column(Integer, default=0)
    error_services = Column(Integer, default=0)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )


class ModuleStatistics(Base):
    """模块统计数据"""
    
    __tablename__ = "module_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, unique=True, index=True)
    module_name = Column(String(100))
    service_count = Column(Integer, default=0)
    user_id = Column(Integer, index=True)
    user_name = Column(String(50))
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )


class ToolStatistics(Base):
    """工具调用统计数据"""
    
    __tablename__ = "tool_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String(100), unique=True, index=True)
    call_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    avg_execution_time = Column(Integer, default=0)  # 毫秒
    last_called_at = Column(DateTime, nullable=True)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )


class ServiceCallStatistics(Base):
    """服务调用统计数据"""
    
    __tablename__ = "service_call_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(String(100), unique=True, index=True)
    service_name = Column(String(100))
    module_name = Column(String(100))
    call_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    ) 