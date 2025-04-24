from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.models.engine import Base, get_db
from app.core.utils import now_beijing
from sqlalchemy.sql import text


class McpService(Base):
    """已发布的MCP服务表"""
    
    __tablename__ = "mcp_services"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, nullable=False, index=True)  # 模块ID
    service_uuid = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(String(20), default="stopped")  # running, stopped, error
    sse_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    enabled = Column(Boolean, default=False)
    
    def get_module_name(self):
        """获取关联的模块名称"""
        with get_db() as db:
            # 使用原生SQL查询避免循环导入
            query = "SELECT name FROM mcp_modules WHERE id = :id"
            sql = text(query).bindparams(id=self.module_id)
            result = db.execute(sql).first()
            return result[0] if result else None
            
    def to_dict(self):
        """转换为字典格式"""
        module_name = self.get_module_name()
        
        return {
            "id": self.id,
            "module_id": self.module_id,
            "module_name": module_name,
            "service_uuid": self.service_uuid,
            "status": self.status,
            "sse_url": self.sse_url,
            "enabled": self.enabled,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            )
        } 