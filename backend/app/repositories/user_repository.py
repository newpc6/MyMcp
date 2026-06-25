"""
用户数据访问层。

Repository 只负责数据库查询，不承载业务校验、外部接口调用或响应封装。
"""
from typing import List, Optional

from sqlalchemy import select

from app.models.engine import get_db
from app.models.modules.users import User


class UserRepository:
    """用户 Repository。"""

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """根据 ID 查询用户。"""
        with get_db() as db:
            query = select(User).where(User.id == user_id)
            return db.execute(query).scalar_one_or_none()

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """根据用户名查询用户。"""
        with get_db() as db:
            query = select(User).where(User.username == username)
            return db.execute(query).scalar_one_or_none()

    @staticmethod
    def get_by_external_id(
        external_id: str,
        platform_type: str
    ) -> Optional[User]:
        """根据外部用户 ID 和平台类型查询用户。"""
        with get_db() as db:
            query = select(User).where(
                User.external_id == external_id,
                User.platform_type == platform_type
            )
            return db.execute(query).scalar_one_or_none()

    @staticmethod
    def list_all() -> List[User]:
        """查询全部用户。"""
        with get_db() as db:
            query = select(User)
            return db.execute(query).scalars().all()
