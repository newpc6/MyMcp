"""
工具执行记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
import json

from app.models.engine import Base
from app.core.utils import now_beijing


class ToolExecution(Base):
    """工具执行记录模型"""
    __tablename__ = "tool_executions"

    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String(100), index=True)
    description = Column(String(500))
    parameters = Column(Text)  # JSON格式存储参数
    result = Column(Text)      # JSON格式存储结果
    status = Column(String(20))  # success 或 failed
    created_at = Column(DateTime, default=now_beijing())
    execution_time = Column(Integer)  # 毫秒

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "description": self.description,
            "parameters": json.loads(self.parameters),
            "result": json.loads(self.result) if self.result else None,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time": self.execution_time
        } 