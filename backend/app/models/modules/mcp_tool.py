from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
import json
from sqlalchemy.sql import text

from app.models.engine import Base, get_db
from app.core.utils import now_beijing


class McpTool(Base):
    """MCP工具信息模型"""
    __tablename__ = "mcp_tools"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, index=True)  # 模块ID
    name = Column(String(100), index=True)  # 工具名称
    function_name = Column(String(100))  # 对应的函数名
    description = Column(Text)  # 工具描述
    parameters = Column(Text)  # 参数定义，JSON格式
    sample_usage = Column(Text)  # 使用示例
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    is_enabled = Column(Boolean, default=True)  # 是否已启用
    
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
        # 解析参数数据
        params = {}
        if self.parameters:
            try:
                params = json.loads(self.parameters)
            except json.JSONDecodeError:
                pass
        
        # 获取模块名称
        module_name = self.get_module_name()
        
        return {
            "id": self.id,
            "module_id": self.module_id,
            "name": self.name,
            "function_name": self.function_name,
            "description": self.description,
            "parameters": params,
            "sample_usage": self.sample_usage,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_enabled": self.is_enabled,
            "module_name": module_name
        } 