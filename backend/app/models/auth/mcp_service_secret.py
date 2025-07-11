"""
MCP服务密钥模型

管理每个MCP服务的访问密钥，支持多密钥管理
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from app.models.engine import Base
from app.core.utils import now_beijing


class McpServiceSecret(Base):
    """MCP服务密钥表"""
    
    __tablename__ = "mcp_service_secrets"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("mcp_services.id"),
                       nullable=False, index=True)
    secret_key = Column(String(255), unique=True, nullable=False, index=True)
    secret_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    # 限制调用次数
    limit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing(),
                       onupdate=now_beijing())
    expires_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    
    def get_creator_name(self):
        """获取创建者用户名"""
        if not self.user_id:
            return None
            
        from app.models.engine import get_db
        from sqlalchemy.sql import text
        
        with get_db() as db:
            query = "SELECT username FROM users WHERE id = :id"
            sql = text(query).bindparams(id=self.user_id)
            result = db.execute(sql).first()
            return result[0] if result else None
    
    def is_expired(self):
        """检查密钥是否已过期"""
        if not self.expires_at:
            return False
        
        from datetime import datetime
        return datetime.now() > self.expires_at
    
    def get_masked_key(self):
        """获取脱敏的密钥（只显示前后几位）"""
        if not self.secret_key or len(self.secret_key) < 8:
            return "****"
        
        return f"{self.secret_key[:4]}****{self.secret_key[-4:]}"
    
    def to_dict(self, include_full_key=False):
        """转换为字典格式
        
        Args:
            include_full_key: 是否包含完整密钥（仅管理员可见）
        """
        return {
            "id": self.id,
            "service_id": self.service_id,
            "secret_key": (self.secret_key if include_full_key
                          else self.get_masked_key()),
            "secret_name": self.secret_name,
            "description": self.description,
            "is_active": self.is_active,
            "limit_count": self.limit_count,
            "is_expired": self.is_expired(),
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S") 
                if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S") 
                if self.updated_at else None
            ),
            "expires_at": (
                self.expires_at.strftime("%Y-%m-%d %H:%M:%S") 
                if self.expires_at else None
            ),
            "user_id": self.user_id,
            "creator_name": self.get_creator_name()
        } 