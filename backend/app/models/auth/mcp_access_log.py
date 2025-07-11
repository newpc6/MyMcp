"""
MCP访问日志模型

记录每次MCP服务的访问详情，用于审计和监控
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.engine import Base
from app.core.utils import now_beijing
import json


class McpAccessLog(Base):
    """MCP访问日志表"""
    
    __tablename__ = "mcp_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("mcp_services.id"),
                       nullable=False, index=True)
    secret_id = Column(Integer, ForeignKey("mcp_service_secrets.id"),
                      nullable=True, index=True)
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    access_time = Column(DateTime, default=now_beijing(), index=True)
    status = Column(String(20), default='success')  # success, error, forbidden
    error_message = Column(Text, nullable=True)
    request_headers = Column(Text, nullable=True)  # JSON格式存储请求头
    
    def get_request_headers_dict(self):
        """获取请求头字典"""
        if not self.request_headers:
            return {}
        
        try:
            return json.loads(self.request_headers)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_request_headers(self, headers_dict):
        """设置请求头（字典转JSON）"""
        if headers_dict:
            self.request_headers = json.dumps(headers_dict, ensure_ascii=False)
        else:
            self.request_headers = None
    
    def get_status_text(self):
        """获取状态文本"""
        status_map = {
            'success': '成功',
            'error': '错误',
            'forbidden': '禁止访问',
            'unauthorized': '未授权'
        }
        return status_map.get(self.status, self.status)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "service_id": self.service_id,
            "secret_id": self.secret_id,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "access_time": (
                self.access_time.strftime("%Y-%m-%d %H:%M:%S") 
                if self.access_time else None
            ),
            "status": self.status,
            "status_text": self.get_status_text(),
            "error_message": self.error_message,
            "request_headers": self.get_request_headers_dict()
        } 