"""
MCP服务密钥管理服务

负责密钥的创建、验证、统计等功能
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date

from app.models.engine import get_db
from app.models.auth.published_service_access_log import McpAccessLog
from app.repositories.mcp_auth_repository import McpAuthRepository
from app.utils.auth.secret_generator import SecretGenerator
from app.utils.logging import mcp_logger
from app.utils.const.error_code import error_code
from app.utils.http.pagination import PageParams


class SecretManager:
    """密钥管理器"""

    # 共享 Repository 实例
    _repo = McpAuthRepository()

    @staticmethod
    def _to_dict_with_creator(
        db, secret: "McpServiceSecret", include_full_key: bool = False
    ) -> Dict[str, Any]:
        """辅助：将密钥转为字典并附带 creator_name。"""
        creator_name = SecretManager._repo.get_creator_name(db, secret.user_id)
        return secret.to_dict(include_full_key=include_full_key,
                              creator_name=creator_name)

    @staticmethod
    def _to_dict_list_with_creators(
        db, secrets: list, include_full_key: bool = False
    ) -> List[Dict[str, Any]]:
        """辅助：批量将密钥列表转为字典并附带 creator_name。"""
        user_ids = [s.user_id for s in secrets if s.user_id is not None]
        names = SecretManager._repo.batch_get_creator_names(db, user_ids)
        return [
            s.to_dict(
                include_full_key=include_full_key,
                creator_name=names.get(s.user_id)
            )
            for s in secrets
        ]

    @staticmethod
    def generate_secret(service_id: int, name: str, description: str = "",
                        limit_count: int = 0,
                        expires_days: int = 0,
                        user_id: Optional[int] = None) -> Dict[str, Any]:
        """生成新密钥

        Args:
            service_id: 服务ID
            name: 密钥名称
            description: 密钥描述
            expires_days: 有效天数，0为永不过期
            user_id: 创建者用户ID

        Returns:
            Dict: 包含密钥信息的字典

        Raises:
            ValueError: 当服务不存在或参数无效时
        """
        with get_db() as db:
            # 检查服务是否存在
            service = SecretManager._repo.get_service_by_id(db, service_id)
            if not service:
                raise ValueError(f"服务不存在: {service_id}")

            # 检查密钥数量限制
            existing_count = SecretManager._repo.count_active_secrets(
                db, service_id)
            max_secrets = 50  # 从配置获取
            if existing_count >= max_secrets:
                raise ValueError(f"服务密钥数量已达上限: {max_secrets}")

            # 生成密钥
            secret_key = SecretGenerator.generate_api_key("mcp", 32)
            expires_at = SecretGenerator.calculate_expiry_date(expires_days)

            # 创建密钥记录
            from app.models.auth.published_service_secret import McpServiceSecret
            secret_record = McpServiceSecret(
                service_id=service_id,
                secret_key=secret_key,
                secret_name=name,
                description=description,
                expires_at=expires_at,
                limit_count=limit_count,
                user_id=user_id
            )

            db.add(secret_record)
            db.commit()
            db.refresh(secret_record)

            mcp_logger.info(f"为服务 {service_id} 生成新密钥: {name}")

            return SecretManager._to_dict_with_creator(
                db, secret_record, include_full_key=True)

    @staticmethod
    def validate_secret(service_id: int,
                        secret: str) -> Optional[Dict[str, Any]]:
        """验证密钥是否有效

        Args:
            service_id: 服务ID
            secret: 密钥字符串

        Returns:
            Optional[Dict]: 如果有效返回密钥信息，否则返回None
        """
        with get_db() as db:
            secret_record = SecretManager._repo.get_secret_by_key(
                db, service_id, secret)

            if not secret_record:
                return error_code.SUCCESS, None

            # 检查是否过期
            if secret_record.is_expired():
                return error_code.AUTH_KEY_EXPIRED, None

            # 检查调用次数限制
            if secret_record.limit_count > 0:
                today_stats = SecretManager._repo.get_today_statistics(
                    db, secret_record.id)
                current_calls = today_stats.call_count if today_stats else 0

                if current_calls >= secret_record.limit_count:
                    msg = (f"MCP服务: {service_id} "
                           f"密钥:{secret_record.secret_key} "
                           f"调用次数已达上限: {secret_record.limit_count}，"
                           f"今日已调用: {current_calls}")
                    mcp_logger.error(msg)
                    return error_code.AUTH_KEY_LIMIT_EXCEEDED, msg

            return error_code.SUCCESS, secret_record.to_dict()

    @staticmethod
    def list_secrets(service_id: int, user_id: Optional[int] = None,
                     is_admin: bool = False) -> List[Dict[str, Any]]:
        """获取服务的密钥列表

        Args:
            service_id: 服务ID
            user_id: 当前用户ID
            is_admin: 是否为管理员

        Returns:
            List[Dict]: 密钥列表
        """
        with get_db() as db:
            service = SecretManager._repo.get_service_by_id(db, service_id)
            if not service:
                return []

            if not is_admin and user_id != service.user_id:
                return []

            secrets = SecretManager._repo.list_all_secrets_by_service(
                db, service_id)
            return SecretManager._to_dict_list_with_creators(
                db, secrets, include_full_key=is_admin)

    @staticmethod
    def delete_secret(secret_id: int, user_id: Optional[int] = None,
                      is_admin: bool = False) -> bool:
        """删除密钥

        Args:
            secret_id: 密钥ID
            user_id: 当前用户ID
            is_admin: 是否为管理员

        Returns:
            bool: 是否删除成功
        """
        with get_db() as db:
            secret = SecretManager._repo.get_secret_by_id(db, secret_id)
            if not secret:
                return False

            service = SecretManager._repo.get_service_by_id(
                db, secret.service_id)
            if not service:
                return False

            if not is_admin and user_id != service.user_id:
                return False

            db.delete(secret)
            db.commit()

            mcp_logger.info(f"删除密钥: {secret_id} ({secret.secret_name})")
            return True

    @staticmethod
    def update_secret(secret_id: int, name: Optional[str] = None,
                      description: Optional[str] = None,
                      is_active: Optional[bool] = None,
                      limit_count: Optional[int] = None,
                      user_id: Optional[int] = None,
                      is_admin: bool = False) -> Optional[Dict[str, Any]]:
        """更新密钥信息

        Args:
            secret_id: 密钥ID
            name: 新名称
            description: 新描述
            is_active: 是否激活
            user_id: 当前用户ID
            is_admin: 是否为管理员

        Returns:
            Optional[Dict]: 更新后的密钥信息
        """
        with get_db() as db:
            secret = SecretManager._repo.get_secret_by_id(db, secret_id)
            if not secret:
                return None

            service = SecretManager._repo.get_service_by_id(
                db, secret.service_id)
            if not service:
                return None

            if not is_admin and user_id != service.user_id:
                return None

            if name is not None:
                secret.secret_name = name
            if description is not None:
                secret.description = description
            if is_active is not None:
                secret.is_active = is_active
            if limit_count is not None and limit_count >= 0:
                secret.limit_count = limit_count
            secret.updated_at = datetime.now()

            db.commit()
            db.refresh(secret)

            mcp_logger.info(f"更新密钥: {secret_id} ({secret.secret_name})")
            return SecretManager._to_dict_with_creator(
                db, secret, include_full_key=is_admin)

    @staticmethod
    def update_secret_statistics(secret_id: int, success: bool = True) -> None:
        """更新密钥访问统计

        Args:
            secret_id: 密钥ID
            success: 是否成功访问
        """
        with get_db() as db:
            try:
                secret = SecretManager._repo.get_secret_by_id(db, secret_id)
                if not secret:
                    return

                today = date.today()
                stats = SecretManager._repo.get_or_create_statistics(
                    db, secret_id, secret.service_id, today)

                stats.increment_call(success)
                db.commit()

            except Exception as e:
                mcp_logger.error(f"更新密钥统计失败: {secret_id}, 错误: {str(e)}")
                db.rollback()

    @staticmethod
    def log_access(service_id: int, secret_id: Optional[int], client_ip: str,
                   user_agent: str, success: bool = True,
                   error_message: str = "",
                   request_headers: Optional[Dict] = None) -> None:
        """记录访问日志

        Args:
            service_id: 服务ID
            secret_id: 密钥ID，可为空（免密访问）
            client_ip: 客户端IP
            user_agent: 用户代理
            success: 是否成功
            error_message: 错误信息
            request_headers: 请求头信息
        """
        with get_db() as db:
            try:
                status = 'success' if success else 'error'

                log_record = McpAccessLog(
                    service_id=service_id,
                    secret_id=secret_id,
                    client_ip=client_ip,
                    user_agent=user_agent,
                    status=status,
                    error_message=error_message if not success else None
                )

                if request_headers:
                    log_record.set_request_headers(request_headers)

                db.add(log_record)
                db.commit()

                if secret_id:
                    SecretManager.update_secret_statistics(secret_id, success)

            except Exception as e:
                mcp_logger.error(f"记录访问日志失败: {str(e)}")
                db.rollback()

    @staticmethod
    def get_secret_statistics(secret_id: int,
                              days: int = 30) -> List[Dict[str, Any]]:
        """获取密钥统计数据

        Args:
            secret_id: 密钥ID
            days: 统计天数

        Returns:
            List[Dict]: 统计数据列表
        """
        with get_db() as db:
            stats = SecretManager._repo.get_statistics_by_secret_id(
                db, secret_id, days=days)
            return [stat.to_dict() for stat in stats]

    @staticmethod
    def get_secret_info(service_id: int, user_id: Optional[int] = None,
                        is_admin: bool = False) -> Dict[str, Any]:
        """获取密钥信息

        Args:
            service_id: 服务ID
            user_id: 当前用户ID
            is_admin: 是否为管理员

        Returns:
            Dict: 密钥信息
        """
        with get_db() as db:
            secrets = SecretManager._repo.list_secrets_by_service(
                db, service_id, is_admin=is_admin, user_id=user_id)
            if not secrets:
                return None

            result = {}
            result['secrets'] = SecretManager._to_dict_list_with_creators(
                db, secrets)
            result['secret_count'] = len(secrets)
            active_secrets = [s for s in secrets if s.is_active]
            result['active_secret_count'] = len(active_secrets)
            inactive_secrets = [s for s in secrets if not s.is_active]
            result['inactive_secret_count'] = len(inactive_secrets)

            # 批量获取统计数据
            secret_ids = [s.id for s in secrets]
            all_stats = SecretManager._repo.get_statistics_by_secret_ids(
                db, secret_ids)
            all_stats_dicts = [stat.to_dict() for stat in all_stats]

            if all_stats_dicts:
                result['total_call_count'] = sum([
                    stat['call_count'] for stat in all_stats_dicts
                ])
                result['total_success_count'] = sum([
                    stat['success_count'] for stat in all_stats_dicts
                ])
                result['total_error_count'] = sum([
                    stat['error_count'] for stat in all_stats_dicts
                ])
                access_times = [
                    stat['last_access_at'] for stat in all_stats_dicts
                    if stat['last_access_at'] is not None
                ]
                result['last_access_time'] = max(
                    access_times) if access_times else None
            else:
                result['total_call_count'] = 0
                result['total_success_count'] = 0
                result['total_error_count'] = 0
                result['last_access_time'] = None

            return result

    @staticmethod
    def get_access_logs(service_id: int, page_params: PageParams,
                        secret_id: Optional[int] = None,
                        status: Optional[str] = None,
                        date_range: Optional[Tuple[date, date]] = None,
                        is_admin: bool = False,
                        user_id: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int]:
        """获取访问日志

        Args:
            service_id: 服务ID
            page_params: 分页参数
            secret_id: 密钥ID，可选

        Returns:
            List[Dict]: 访问日志列表
        """
        with get_db() as db:
            logs, total = SecretManager._repo.query_access_logs(
                db, service_id, page_params,
                secret_id=secret_id, status=status, date_range=date_range)
            logs_list = [log.to_dict() for log in logs]

            # 批量补充密钥名称
            secret_ids = [log['secret_id'] for log in logs_list]
            secrets_dict = SecretManager._repo.batch_get_secret_names(
                db, secret_ids)
            for log in logs_list:
                log['secret_name'] = secrets_dict.get(log['secret_id'])

            # 批量补充服务名称
            service_ids = [log['service_id'] for log in logs_list]
            services_dict = SecretManager._repo.batch_get_service_names(
                db, service_ids)
            for log in logs_list:
                log['service_name'] = services_dict.get(log['service_id'])

            return logs_list, total
