"""
分组相关模型

Model 层只定义 ORM 结构和序列化，不包含数据库查询副作用。
统计查询已迁移至 app.repositories.mcp_template_group_repository。
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime
)

from app.models.engine import Base
from app.core.utils import now_beijing


class McpGroup(Base):
    """MCP分组信息模型"""
    __tablename__ = "mcp_template_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True)  # 分组名称
    description = Column(Text, nullable=True)  # 分组描述
    icon = Column(String(200), nullable=True)  # 分组图标
    order = Column(Integer, default=0)  # 排序序号
    created_at = Column(DateTime, default=now_beijing())
    updated_at = Column(DateTime, default=now_beijing())
    user_id = Column(Integer, nullable=True, index=True)  # 创建者ID

    def to_dict(self, templates_count=None, include_modules_count=True):
        """转换为字典格式。

        参数:
            templates_count: 由外部（Service/Repository）传入的模板计数，
                             避免在 Model 层打开数据库连接。
            include_modules_count: 兼容旧调用参数；Model 层不再自行查询，
                                   未传 templates_count 时返回 0。
        """
        modules_count = (
            templates_count
            if include_modules_count and templates_count is not None
            else 0
        )
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
