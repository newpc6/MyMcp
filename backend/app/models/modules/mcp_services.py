from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from app.models.engine import Base, get_db
from app.core.utils import now_beijing
from sqlalchemy.sql import text
import json


class McpService(Base):
    """已发布的MCP服务表"""
    
    __tablename__ = "mcp_services"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, nullable=True, index=True)  # 模块ID，第三方服务时为空
    service_uuid = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)  # 服务名称
    status = Column(String(20), default="stopped")  # running, stopped, error
    error_message = Column(Text, nullable=True)  # 错误信息
    sse_url = Column(String(255), nullable=False)
    protocol_type = Column(Integer, default=1)  # 协议类型：1=SSE, 2=流式HTTP
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    enabled = Column(Boolean, default=False)
    user_id = Column(Integer, nullable=True, index=True)  # 创建者用户ID
    config_params = Column(Text, nullable=True)  # 存储服务配置参数，包括密钥信息等
    is_public = Column(Boolean, default=False)  # 是否公开，True为公开，False为私有
    service_type = Column(Integer, default=1)  # 服务类型：1=内置服务(基于模板), 2=第三方服务
    description = Column(Text, nullable=True)  # 服务描述，第三方服务时使用
    
    def get_module_name(self):
        """获取关联的模块名称"""
        if not self.module_id:
            return "第三方服务"
            
        with get_db() as db:
            # 使用原生SQL查询避免循环导入
            query = "SELECT name FROM mcp_modules WHERE id = :id"
            sql = text(query).bindparams(id=self.module_id)
            result = db.execute(sql).first()
            return result[0] if result else None
            
    def get_user_name(self):
        """获取创建者用户名"""
        if not self.user_id:
            return None
            
        with get_db() as db:
            # 使用原生SQL查询避免循环导入
            query = "SELECT username FROM users WHERE id = :id"
            sql = text(query).bindparams(id=self.user_id)
            result = db.execute(sql).first()
            return result[0] if result else None
    
    def get_service_type_name(self):
        """获取服务类型名称"""
        type_map = {
            1: "内置服务",
            2: "第三方服务"
        }
        return type_map.get(self.service_type, "未知类型")
            
    def to_dict(self, module_info=None, user_info=None):
        """转换为字典格式
        
        Args:
            module_info: 模块信息字典 {module_id: {'name': str, 'description': str}}
            user_info: 用户信息字典 {user_id: {'username': str}}
        """
        # 获取模块名称
        if self.module_id and module_info and self.module_id in module_info:
            module_name = module_info[self.module_id]['name']
        else:
            module_name = self.get_module_name()
        
        # 获取用户名称
        if self.user_id and user_info and self.user_id in user_info:
            user_name = user_info[self.user_id]['username']
        else:
            user_name = self.get_user_name()
        
        service_type_name = self.get_service_type_name()
        
        # 解析config_params JSON字符串
        config_params = None
        if self.config_params:
            try:
                config_params = json.loads(self.config_params)
            except (json.JSONDecodeError, TypeError):
                # 如果解析失败，返回空字典
                config_params = {}
        else:
            config_params = {}
        
        return {
            "id": self.id,
            "module_id": self.module_id,
            "module_name": module_name,
            "service_uuid": self.service_uuid,
            "name": self.name,
            "status": self.status,
            "sse_url": self.sse_url,
            "enabled": self.enabled,
            "user_id": self.user_id,
            "user_name": user_name,
            "config_params": config_params,
            "error_message": self.error_message,
            "protocol_type": self.protocol_type,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S") 
                if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S") 
                if self.updated_at else None
            ),
            "is_public": self.is_public,
            "service_type": self.service_type,
            "service_type_name": service_type_name,
            "description": self.description
        } 