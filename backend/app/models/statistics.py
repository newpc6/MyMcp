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
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "total_services": self.total_services,
            "running_services": self.running_services,
            "stopped_services": self.stopped_services,
            "error_services": self.error_services,
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.updated_at else None
            )
        }


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
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "module_id": self.module_id,
            "module_name": self.module_name,
            "service_count": self.service_count,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.updated_at else None
            )
        }


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
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "call_count": self.call_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "avg_execution_time": self.avg_execution_time,
            "last_called_at": (
                self.last_called_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.last_called_at else None
            ),
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.updated_at else None
            )
        }


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
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "service_id": self.service_id,
            "service_name": self.service_name,
            "module_name": self.module_name,
            "call_count": self.call_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.updated_at else None
            )
        } 