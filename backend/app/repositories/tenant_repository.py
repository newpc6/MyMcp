"""
租户数据访问层。

Repository 只负责数据库查询，不承载业务校验、外部接口调用或响应封装。
"""
from typing import Dict, List, Optional

from sqlalchemy import select

from app.models.engine import get_db
from app.models.modules.users import Tenant, User, UserTenant


class TenantRepository:
    """租户 Repository。"""

    @staticmethod
    def get_by_id(tenant_id: int) -> Optional[Tenant]:
        """根据 ID 查询租户。"""
        with get_db() as db:
            query = select(Tenant).where(Tenant.id == tenant_id)
            return db.execute(query).scalar_one_or_none()

    @staticmethod
    def get_by_code(code: str) -> Optional[Tenant]:
        """根据编码查询租户。"""
        with get_db() as db:
            query = select(Tenant).where(Tenant.code == code)
            return db.execute(query).scalar_one_or_none()

    @staticmethod
    def list_all() -> List[Tenant]:
        """查询全部租户。"""
        with get_db() as db:
            query = select(Tenant)
            return db.execute(query).scalars().all()

    @staticmethod
    def list_by_user_id(user_id: int) -> List[Tenant]:
        """查询用户关联的租户。"""
        with get_db() as db:
            user = db.execute(
                select(User).where(User.id == user_id)
            ).scalar_one_or_none()
            if not user:
                return []

            query = (
                select(Tenant)
                .join(UserTenant)
                .where(UserTenant.user_id == user_id)
            )
            return db.execute(query).scalars().all()

    @staticmethod
    def list_by_user_ids(user_ids: List[int]) -> Dict[int, List[Tenant]]:
        """批量查询多个用户关联的租户。"""
        if not user_ids:
            return {}

        with get_db() as db:
            query = (
                select(UserTenant.user_id, Tenant)
                .join(Tenant, UserTenant.tenant_id == Tenant.id)
                .where(UserTenant.user_id.in_(user_ids))
            )
            results = db.execute(query).all()

            user_tenants: Dict[int, List[Tenant]] = {
                user_id: [] for user_id in user_ids
            }
            for user_id, tenant in results:
                user_tenants[user_id].append(tenant)

            return user_tenants
