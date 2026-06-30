"""
已发布 MCP 服务密钥模型

管理每个已发布 MCP 服务的访问密钥，支持多密钥管理
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from app.models.engine import Base
from app.core.utils import now_beijing


class McpServiceSecret(Base):
    """已发布 MCP 服务密钥表"""

    __tablename__ = "published_service_secrets"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("published_services.id"),
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
        """获取创建者用户名（需由调用方通过 Repository 查询后传入 to_dict）。

        模型层不再自行打开数据库连接；返回 None 避免隐式副作用。
        """
        return None

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

    def to_dict(self, include_full_key=False, creator_name=None):
        """转换为字典格式

        Args:
            include_full_key: 是否包含完整密钥（仅管理员可见）
            creator_name: 创建者用户名，由调用方通过 Repository 查询传入。
                          为 None 时回退到 get_creator_name()（已移除 DB 副作用）。
        """
        name = creator_name if creator_name is not None else self.get_creator_name()
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
            "creator_name": name
        }
