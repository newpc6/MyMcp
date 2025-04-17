"""
活动记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime

from app.models.engine import Base
from app.core.utils import now_beijing


class Activity(Base):
    """活动记录模型"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(String(50), index=True)
    description = Column(String(500))
    created_at = Column(DateTime, default=now_beijing())

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "activity_type": self.activity_type,
            "description": self.description,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } 