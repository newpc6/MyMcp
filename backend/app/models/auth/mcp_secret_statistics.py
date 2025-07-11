"""
MCP密钥访问统计模型

记录每个密钥的访问统计信息，按日期聚合
"""

from sqlalchemy import (Column, Integer, DateTime, Date, ForeignKey, 
                        UniqueConstraint)
from sqlalchemy.orm import relationship
from app.models.engine import Base
from app.core.utils import now_beijing
from datetime import datetime, date


class McpSecretStatistics(Base):
    """MCP密钥访问统计表"""
    
    __tablename__ = "mcp_secret_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    secret_id = Column(Integer, ForeignKey("mcp_service_secrets.id"), 
                      nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("mcp_services.id"), 
                       nullable=False, index=True)
    call_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_access_at = Column(DateTime, nullable=True)
    statistics_date = Column(Date, default=date.today, index=True)
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing(), 
                       onupdate=now_beijing())
    
    
    # 唯一约束：每个密钥每天只有一条统计记录
    __table_args__ = (
        UniqueConstraint('secret_id', 'statistics_date', 
                        name='uq_secret_statistics_date'),
    )
    
    def get_success_rate(self):
        """计算成功率"""
        if self.call_count == 0:
            return 0.0
        return round((self.success_count / self.call_count) * 100, 2)
    
    def get_error_rate(self):
        """计算错误率"""
        if self.call_count == 0:
            return 0.0
        return round((self.error_count / self.call_count) * 100, 2)
    
    def increment_call(self, success=True):
        """增加调用计数
        
        Args:
            success: 是否成功调用
        """
        if self.call_count is None:
            self.call_count = 0
        if self.success_count is None:
            self.success_count = 0
        if self.error_count is None:
            self.error_count = 0
        
        self.call_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        self.last_access_at = datetime.now()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "secret_id": self.secret_id,
            "service_id": self.service_id,
            "call_count": self.call_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.get_success_rate(),
            "error_rate": self.get_error_rate(),
            "last_access_at": (
                self.last_access_at.strftime("%Y-%m-%d %H:%M:%S") 
                if self.last_access_at else None
            ),
            "statistics_date": (
                self.statistics_date.strftime("%Y-%m-%d") 
                if self.statistics_date else None
            ),
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S") 
                if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S") 
                if self.updated_at else None
            )
        } 