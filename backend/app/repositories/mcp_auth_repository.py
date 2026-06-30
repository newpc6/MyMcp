"""
MCP 鉴权/密钥数据访问层。

Repository 只负责数据库查询和持久化辅助，不承载业务校验、权限判断
或响应封装。事务和 Session 生命周期由 Service 层控制。
"""
from typing import Dict, List, Optional, Tuple
from datetime import date

from sqlalchemy import and_, bindparam, text
from sqlalchemy.orm import Session

from app.models.modules.published_service import McpService
from app.models.auth.published_service_secret import McpServiceSecret
from app.models.auth.published_service_secret_statistics import McpSecretStatistics
from app.models.auth.published_service_access_log import McpAccessLog
from app.utils.http.pagination import PageParams


class McpAuthRepository:
    """MCP 鉴权/密钥 Repository。"""

    # ------------------------------------------------------------------
    # 服务查询
    # ------------------------------------------------------------------

    @staticmethod
    def get_service_by_id(db: Session, service_id: int) -> Optional[McpService]:
        """根据 ID 查询已发布服务。"""
        return db.query(McpService).filter(
            McpService.id == service_id
        ).first()

    # ------------------------------------------------------------------
    # 密钥查询
    # ------------------------------------------------------------------

    @staticmethod
    def count_active_secrets(db: Session, service_id: int) -> int:
        """统计服务下活跃密钥数量。"""
        return db.query(McpServiceSecret).filter(
            and_(
                McpServiceSecret.service_id == service_id,
                McpServiceSecret.is_active.is_(True)
            )
        ).count()

    @staticmethod
    def get_secret_by_key(
        db: Session, service_id: int, secret_key: str
    ) -> Optional[McpServiceSecret]:
        """根据服务ID + 密钥字符串查询有效密钥记录。"""
        return db.query(McpServiceSecret).filter(
            and_(
                McpServiceSecret.service_id == service_id,
                McpServiceSecret.secret_key == secret_key,
                McpServiceSecret.is_active.is_(True)
            )
        ).first()

    @staticmethod
    def get_secret_by_id(
        db: Session, secret_id: int
    ) -> Optional[McpServiceSecret]:
        """根据密钥 ID 查询密钥。"""
        return db.query(McpServiceSecret).filter(
            McpServiceSecret.id == secret_id
        ).first()

    @staticmethod
    def list_secrets_by_service(
        db: Session,
        service_id: int,
        is_admin: bool = False,
        user_id: Optional[int] = None,
        order_desc: bool = True,
    ) -> List[McpServiceSecret]:
        """按服务 ID 列出密钥，支持权限过滤。

        非管理员仅返回自己的密钥或无主密钥。
        """
        query = db.query(McpServiceSecret).filter(
            McpServiceSecret.service_id == service_id
        )
        if not is_admin:
            query = query.where(
                (McpServiceSecret.user_id == user_id)
                | (McpServiceSecret.user_id.is_(None))
            )
        if order_desc:
            query = query.order_by(McpServiceSecret.created_at.desc())
        return query.all()

    @staticmethod
    def list_all_secrets_by_service(
        db: Session, service_id: int
    ) -> List[McpServiceSecret]:
        """按服务 ID 列出所有密钥（无权限过滤）。"""
        return db.query(McpServiceSecret).filter(
            McpServiceSecret.service_id == service_id
        ).order_by(McpServiceSecret.created_at.desc()).all()

    @staticmethod
    def batch_get_secret_names(
        db: Session, secret_ids: List[int]
    ) -> Dict[int, str]:
        """批量获取密钥名称映射。"""
        if not secret_ids:
            return {}
        secrets = db.query(McpServiceSecret).filter(
            McpServiceSecret.id.in_(secret_ids)
        ).all()
        return {s.id: s.secret_name for s in secrets}

    # ------------------------------------------------------------------
    # 统计查询
    # ------------------------------------------------------------------

    @staticmethod
    def get_today_statistics(
        db: Session, secret_id: int
    ) -> Optional[McpSecretStatistics]:
        """获取密钥今日统计记录。"""
        today = date.today()
        return db.query(McpSecretStatistics).filter(
            and_(
                McpSecretStatistics.secret_id == secret_id,
                McpSecretStatistics.statistics_date == today
            )
        ).first()

    @staticmethod
    def get_or_create_statistics(
        db: Session,
        secret_id: int,
        service_id: int,
        statistics_date: date,
    ) -> McpSecretStatistics:
        """获取或创建密钥统计记录（仅 flush，不 commit）。"""
        stats = db.query(McpSecretStatistics).filter(
            and_(
                McpSecretStatistics.secret_id == secret_id,
                McpSecretStatistics.statistics_date == statistics_date
            )
        ).first()
        if not stats:
            stats = McpSecretStatistics(
                secret_id=secret_id,
                service_id=service_id,
                statistics_date=statistics_date
            )
            db.add(stats)
            db.flush()
        return stats

    @staticmethod
    def get_statistics_by_secret_id(
        db: Session, secret_id: int, days: int = 30
    ) -> List[McpSecretStatistics]:
        """按密钥 ID 获取最近 N 天统计记录。"""
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days)
        return db.query(McpSecretStatistics).filter(
            and_(
                McpSecretStatistics.secret_id == secret_id,
                McpSecretStatistics.statistics_date >= start_date,
                McpSecretStatistics.statistics_date <= end_date
            )
        ).order_by(McpSecretStatistics.statistics_date.desc()).all()

    @staticmethod
    def get_statistics_by_secret_ids(
        db: Session, secret_ids: List[int]
    ) -> List[McpSecretStatistics]:
        """按多个密钥 ID 获取所有统计记录。"""
        if not secret_ids:
            return []
        return db.query(McpSecretStatistics).filter(
            McpSecretStatistics.secret_id.in_(secret_ids)
        ).all()

    # ------------------------------------------------------------------
    # 访问日志查询
    # ------------------------------------------------------------------

    @staticmethod
    def query_access_logs(
        db: Session,
        service_id: int,
        page_params: PageParams,
        secret_id: Optional[int] = None,
        status: Optional[str] = None,
        date_range: Optional[Tuple[date, date]] = None,
    ) -> Tuple[List[McpAccessLog], int]:
        """分页查询访问日志。

        返回:
            (日志列表, 总数)
        """
        query = db.query(McpAccessLog)
        if service_id != 0:
            query = query.filter(McpAccessLog.service_id == service_id)
        if secret_id:
            query = query.filter(McpAccessLog.secret_id == secret_id)
        if status:
            query = query.filter(McpAccessLog.status == status)
        if date_range:
            query = query.filter(
                McpAccessLog.access_time >= date_range[0],
                McpAccessLog.access_time <= date_range[1]
            )
        total = query.count()
        query = query.order_by(
            McpAccessLog.access_time.desc()
        ).offset(page_params.offset).limit(page_params.size)
        return query.all(), total

    @staticmethod
    def batch_get_service_names(
        db: Session, service_ids: List[int]
    ) -> Dict[int, str]:
        """批量获取服务名称映射。"""
        if not service_ids:
            return {}
        services = db.query(McpService).filter(
            McpService.id.in_(service_ids)
        ).all()
        return {s.id: s.name for s in services}

    # ------------------------------------------------------------------
    # 用户查询
    # ------------------------------------------------------------------

    @staticmethod
    def get_creator_name(
        db: Session, user_id: Optional[int]
    ) -> Optional[str]:
        """获取创建者用户名。"""
        if not user_id:
            return None
        result = db.execute(
            text("SELECT username FROM users WHERE id = :id"),
            {"id": user_id}
        ).first()
        return result[0] if result else None

    @staticmethod
    def batch_get_creator_names(
        db: Session, user_ids: List[int]
    ) -> Dict[int, str]:
        """批量获取创建者用户名映射。"""
        unique_ids = [uid for uid in set(user_ids) if uid is not None]
        if not unique_ids:
            return {}
        sql = text(
            "SELECT id, username FROM users WHERE id IN :ids"
        ).bindparams(bindparam("ids", expanding=True))
        rows = db.execute(sql, {"ids": unique_ids}).fetchall()
        return {row[0]: row[1] for row in rows}
