"""
MCP服务密钥管理服务

负责密钥的创建、验证、统计等功能
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from sqlalchemy import and_

from app.models.engine import get_db
from app.models.modules.mcp_services import McpService
from app.models.auth.mcp_service_secret import McpServiceSecret
from app.models.auth.mcp_secret_statistics import McpSecretStatistics
from app.models.auth.mcp_access_log import McpAccessLog
from app.utils.auth.secret_generator import SecretGenerator
from app.utils.logging import mcp_logger
from app.utils.const.error_code import error_code
from app.utils.http.pagination import PageParams


class SecretManager:
    """密钥管理器"""

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
            service = db.query(McpService).filter(
                McpService.id == service_id
            ).first()
            if not service:
                raise ValueError(f"服务不存在: {service_id}")

            # 检查密钥数量限制
            existing_count = db.query(McpServiceSecret).filter(
                and_(
                    McpServiceSecret.service_id == service_id,
                    McpServiceSecret.is_active.is_(True)
                )
            ).count()

            # 这里可以配置最大密钥数量
            max_secrets = 50  # 从配置获取
            if existing_count >= max_secrets:
                raise ValueError(f"服务密钥数量已达上限: {max_secrets}")

            # 生成密钥
            secret_key = SecretGenerator.generate_api_key("mcp", 32)
            expires_at = SecretGenerator.calculate_expiry_date(expires_days)

            # 创建密钥记录
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

            return secret_record.to_dict(include_full_key=True)

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
            secret_record = db.query(McpServiceSecret).filter(
                and_(
                    McpServiceSecret.service_id == service_id,
                    McpServiceSecret.secret_key == secret,
                    McpServiceSecret.is_active.is_(True)
                )
            ).first()

            if not secret_record:
                return error_code.SUCCESS, None

            # 检查是否过期
            if secret_record.is_expired():
                return error_code.AUTH_KEY_EXPIRED, None

            # 检查调用次数限制
            if secret_record.limit_count > 0:
                # 获取今日调用次数
                today = date.today()
                today_stats = db.query(McpSecretStatistics).filter(
                    and_(
                        McpSecretStatistics.secret_id == secret_record.id,
                        McpSecretStatistics.statistics_date == today
                    )
                ).first()
                
                current_calls = today_stats.call_count if today_stats else 0
                
                # 如果设置了限制且当前调用次数已达到限制，则拒绝访问
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
            # 检查权限
            service = db.query(McpService).filter(
                McpService.id == service_id
            ).first()

            if not service:
                return []

            # 非管理员只能查看自己创建的服务的密钥
            if not is_admin and user_id != service.user_id:
                return []

            secrets = db.query(McpServiceSecret).filter(
                McpServiceSecret.service_id == service_id
            ).order_by(McpServiceSecret.created_at.desc()).all()

            return [secret.to_dict(include_full_key=is_admin)
                    for secret in secrets]

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
            secret = db.query(McpServiceSecret).filter(
                McpServiceSecret.id == secret_id
            ).first()

            if not secret:
                return False

            # 检查权限
            service = db.query(McpService).filter(
                McpService.id == secret.service_id
            ).first()

            if not service:
                return False

            # 非管理员只能删除自己创建的服务的密钥
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
            secret = db.query(McpServiceSecret).filter(
                McpServiceSecret.id == secret_id
            ).first()

            if not secret:
                return None

            # 检查权限
            service = db.query(McpService).filter(
                McpService.id == secret.service_id
            ).first()

            if not service:
                return None

            # 非管理员只能修改自己创建的服务的密钥
            if not is_admin and user_id != service.user_id:
                return None

            # 更新字段
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
            return secret.to_dict(include_full_key=is_admin)

    @staticmethod
    def update_secret_statistics(secret_id: int, success: bool = True) -> None:
        """更新密钥访问统计

        Args:
            secret_id: 密钥ID
            success: 是否成功访问
        """
        with get_db() as db:
            try:
                # 获取密钥信息
                secret = db.query(McpServiceSecret).filter(
                    McpServiceSecret.id == secret_id
                ).first()

                if not secret:
                    return

                today = date.today()

                # 查找或创建今日统计记录
                stats = db.query(McpSecretStatistics).filter(
                    and_(
                        McpSecretStatistics.secret_id == secret_id,
                        McpSecretStatistics.statistics_date == today
                    )
                ).first()

                if not stats:
                    stats = McpSecretStatistics(
                        secret_id=secret_id,
                        service_id=secret.service_id,
                        statistics_date=today
                    )
                    db.add(stats)

                # 更新统计
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

                # 如果有密钥，更新统计
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
            end_date = date.today()
            start_date = date.fromordinal(end_date.toordinal() - days)

            stats = db.query(McpSecretStatistics).filter(
                and_(
                    McpSecretStatistics.secret_id == secret_id,
                    McpSecretStatistics.statistics_date >= start_date,
                    McpSecretStatistics.statistics_date <= end_date
                )
            ).order_by(McpSecretStatistics.statistics_date.desc()).all()

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
            query = db.query(McpServiceSecret).filter(
                McpServiceSecret.service_id == service_id
            )
            if is_admin:
                pass
            else:
                query = query.where((McpServiceSecret.user_id == user_id)
                                    | (McpServiceSecret.user_id.is_(None)))
            
            secrets = query.all()
            if not secrets:
                return None
            result = {}
            result['secrets'] = [secret.to_dict() for secret in secrets]
            result['secret_count'] = len(secrets)
            active_secrets = [secret for secret in secrets if secret.is_active]
            result['active_secret_count'] = len(active_secrets)
            inactive_secrets = [secret for secret in secrets if not secret.is_active]
            result['inactive_secret_count'] = len(inactive_secrets)
            secrets_statistics = {}
            for secret in secrets:
                stats = SecretManager.get_secret_statistics(secret.id)
                secrets_statistics[secret.id] = stats
            
            # 计算统计数据，处理空列表的情况
            all_stats = []
            for stats_list in secrets_statistics.values():
                all_stats.extend(stats_list)
            
            if all_stats:
                result['total_call_count'] = sum([
                    stat['call_count'] for stat in all_stats
                ])
                result['total_success_count'] = sum([
                    stat['success_count'] for stat in all_stats
                ])
                result['total_error_count'] = sum([
                    stat['error_count'] for stat in all_stats
                ])
                # 过滤掉None值，避免max函数错误
                access_times = [
                    stat['last_access_at'] for stat in all_stats 
                    if stat['last_access_at'] is not None
                ]
                result['last_access_time'] = max(access_times) if access_times else None
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
                        date_range: Optional[Tuple[date, date]] = None) -> Tuple[List[Dict[str, Any]], int]:
        """获取访问日志

        Args:
            service_id: 服务ID
            page_params: 分页参数
            secret_id: 密钥ID，可选

        Returns:
            List[Dict]: 访问日志列表
        """
        with get_db() as db:
            query = db.query(McpAccessLog).filter(
                McpAccessLog.service_id == service_id
            )

            if secret_id:
                query = query.filter(McpAccessLog.secret_id == secret_id)
            if status:
                query = query.filter(McpAccessLog.status == status)
            if date_range:
                query = query.filter(McpAccessLog.access_time >= date_range[0], McpAccessLog.access_time <= date_range[1])
            total = query.count()
            query = query.order_by(
                McpAccessLog.access_time.desc()
            ).offset(page_params.offset).limit(page_params.size)
            logs = query.all()
            logs_list = [log.to_dict() for log in logs]
            secert_ids = [log['secret_id'] for log in logs_list]
            secrets = db.query(McpServiceSecret).filter(
                McpServiceSecret.id.in_(secert_ids)
            ).all()
            secrets_dict = {secret.id: secret.secret_name for secret in secrets}
            for log in logs_list:
                log['secret_name'] = secrets_dict.get(log['secret_id'])
            return logs_list, total
