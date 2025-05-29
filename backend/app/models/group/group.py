"""
分组相关模型
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime
)
from sqlalchemy.sql import text

from app.models.engine import Base, get_db
from app.core.utils import now_beijing


class McpGroup(Base):
    """MCP分组信息模型"""
    __tablename__ = "mcp_group"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True)  # 分组名称
    description = Column(Text, nullable=True)  # 分组描述
    icon = Column(String(200), nullable=True)  # 分组图标
    order = Column(Integer, default=0)  # 排序序号
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    user_id = Column(Integer, nullable=True, index=True)  # 创建者ID

    def to_dict(self):
        """转换为字典格式"""
        # 获取模块数量通过直接查询
        with get_db() as db:
            # 使用原生SQL查询避免循环导入
            query = "SELECT COUNT(*) FROM mcp_modules WHERE category_id = :id"
            sql = text(query).bindparams(id=self.id)
            modules_count = db.execute(sql).scalar()

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "order": self.order,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "modules_count": modules_count,
            "user_id": self.user_id
        }
