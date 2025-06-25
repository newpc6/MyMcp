"""
统计模型

用于存储和查询MCP服务和工具调用统计数据
"""

from sqlalchemy import Column, Integer, String, DateTime, Date
from datetime import datetime, date

from .engine import Base


class ServiceStatistics(Base):
    """MCP服务统计数据"""
    
    __tablename__ = "service_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 统计日期
    statistics_date = Column(Date, default=date.today, index=True)
    
    # MCP模板分组统计
    total_template_groups = Column(Integer, default=0)
    today_new_template_groups = Column(Integer, default=0)
    
    # MCP模板统计
    total_templates = Column(Integer, default=0)
    today_new_templates = Column(Integer, default=0)
    
    # MCP服务调用统计
    total_service_calls = Column(Integer, default=0)
    today_new_service_calls = Column(Integer, default=0)
    
    # MCP服务调用成功失败统计
    today_service_calls_success = Column(Integer, default=0)
    today_service_calls_error = Column(Integer, default=0)
    
    # MCP工具调用统计
    total_tools_calls = Column(Integer, default=0)
    today_new_tools_calls = Column(Integer, default=0)
    
    # MCP服务调用成功失败统计
    today_tools_calls_success = Column(Integer, default=0)
    today_tools_calls_error = Column(Integer, default=0)
    
    # MCP发布服务统计
    total_services = Column(Integer, default=0)
    running_services = Column(Integer, default=0)
    stopped_services = Column(Integer, default=0)
    error_services = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "statistics_date": (
                self.statistics_date.strftime("%Y-%m-%d")
                if self.statistics_date else None
            ),
            "total_template_groups": self.total_template_groups,
            "today_new_template_groups": self.today_new_template_groups,
            "total_templates": self.total_templates,
            "today_new_templates": self.today_new_templates,
            "total_service_calls": self.total_service_calls,
            "today_new_service_calls": self.today_new_service_calls,
            "today_service_calls_success": self.today_service_calls_success,
            "today_service_calls_error": self.today_service_calls_error,
            "total_tools_calls": self.total_tools_calls,
            "today_new_tools_calls": self.today_new_tools_calls,
            "today_tools_calls_success": self.today_tools_calls_success,
            "today_tools_calls_error": self.today_tools_calls_error,
            "total_services": self.total_services,
            "running_services": self.running_services,
            "stopped_services": self.stopped_services,
            "error_services": self.error_services,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.created_at else None
            ),
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