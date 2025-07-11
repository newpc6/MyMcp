"""
MCP认证中间件

处理MCP服务的认证和授权
"""

import re
from typing import Optional, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.models.engine import get_db
from app.models.modules.mcp_services import McpService
from app.models.auth.mcp_service_secret import McpServiceSecret
from app.models.auth.mcp_secret_statistics import McpSecretStatistics
from app.services.auth.secret_manager import SecretManager
from app.utils.logging import mcp_logger
from sqlalchemy import and_
from datetime import date

from app.utils.response import success_response, error_response
from app.utils.const.error_code import error_code


class McpAuthMiddleware(BaseHTTPMiddleware):
    """MCP认证中间件"""

    def __init__(self, app):
        super().__init__(app)
        # MCP服务路径正则模式
        self.mcp_pattern = re.compile(r'^/mcp-([a-f0-9\-]+)(/|$)')
        self.custom_mcp_pattern = re.compile(
            r'^/mcp(/.*)?(/sse|/stream|/messages)/?$'
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求拦截"""
        path = request.url.path

        # 检查是否为MCP服务请求
        if not self._is_mcp_request(path):
            return await call_next(request)

        # 提取服务信息
        service_info = self._extract_service_info(path, request)
        if not service_info:
            return await call_next(request)

        service_id = service_info.get('service_id')

        # 检查服务鉴权配置
        auth_result, secret_info = self._check_service_auth(
            service_id, request)

        # 记录访问日志
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get('user-agent', '')
        request_headers = dict(request.headers)

        if auth_result == error_code.SUCCESS:
            # 鉴权成功，记录成功日志
            SecretManager.log_access(
                service_id=service_id,
                secret_id=secret_info.get('id'),
                client_ip=client_ip,
                user_agent=user_agent,
                success=True,
                request_headers=request_headers
            )

            # 继续处理请求
            return await call_next(request)
        else:
            # 鉴权失败，记录失败日志
            SecretManager.log_access(
                service_id=service_id,
                secret_id=None,
                client_ip=client_ip,
                user_agent=user_agent,
                success=False,
                error_message='鉴权失败',
                request_headers=request_headers
            )

            # 返回鉴权失败响应
            return error_response(
                message=error_code.to_message(auth_result) if secret_info is None or isinstance(
                    secret_info, str) is False else secret_info,
                code=auth_result,
                http_status_code=401
            )

    def _is_mcp_request(self, path: str) -> bool:
        """检查是否为MCP服务请求"""
        # 标准MCP路径: /mcp-{uuid}/sse 或 /mcp-{uuid}/stream
        if self.mcp_pattern.match(path):
            return True

        # 自定义MCP路径: /mcp/custom/path/sse 或 完全自定义路径
        if self.custom_mcp_pattern.match(path):
            return True

        # 检查是否为完全自定义路径（从数据库查询）
        return self._is_custom_service_path(path)

    def _is_custom_service_path(self, path: str) -> bool:
        """检查是否为完全自定义的服务路径"""
        try:
            with get_db() as db:
                # 查询是否有服务使用此自定义路径
                service = db.query(McpService).filter(
                    McpService.sse_url == path
                ).first()
                return service is not None
        except Exception:
            return False

    def _extract_service_info(self, path: str,
                              request: Request) -> Optional[Dict[str, Any]]:
        """提取服务信息"""
        try:
            with get_db() as db:
                # 直接通过路径查找服务
                service = db.query(McpService).filter(
                    McpService.sse_url == path
                ).first()

                if not service:
                    # 尝试匹配标准路径模式
                    match = self.mcp_pattern.match(path)
                    if match:
                        service_uuid = match.group(1)
                        service = db.query(McpService).filter(
                            McpService.service_uuid == service_uuid
                        ).first()

                if service:
                    return {
                        'service_id': service.id,
                        'service_uuid': service.service_uuid,
                        'service': service
                    }

                return None
        except Exception as e:
            mcp_logger.error(f"提取服务信息失败: {str(e)}")
            return None

    def _check_service_auth(self, service_id: int,
                            request: Request) -> tuple[int, str]:
        """检查服务鉴权"""
        try:
            with get_db() as db:
                service = db.query(McpService).filter(
                    McpService.id == service_id
                ).first()

                if not service:
                    return error_code.HTTP_NOT_FOUND, ''

                # 如果不需要鉴权或鉴权模式为空，直接通过
                if not service.auth_required or not service.auth_mode:
                    return error_code.SUCCESS, ''

                # 提取密钥
                secret = self._extract_auth_header(request)
                if not secret:
                    secret = self._extract_auth_query(request)

                if not secret:
                    return error_code.AUTH_KEY_REQUIRED, ''

                # 验证密钥
                result, secret_info = SecretManager.validate_secret(
                    service_id, secret)

                if result != error_code.SUCCESS:
                    return result, secret_info

                if not secret_info:
                    # 检查是否是调用次数超限
                    secret_record = db.query(McpServiceSecret).filter(
                        and_(
                            McpServiceSecret.service_id == service_id,
                            McpServiceSecret.secret_key == secret,
                            McpServiceSecret.is_active.is_(True)
                        )
                    ).first()

                    if secret_record and secret_record.limit_count > 0:
                        # 获取今日调用次数
                        today = date.today()
                        today_stats = db.query(McpSecretStatistics).filter(
                            and_(
                                McpSecretStatistics.secret_id ==
                                secret_record.id,
                                McpSecretStatistics.statistics_date == today
                            )
                        ).first()

                        current_calls = (today_stats.call_count
                                         if today_stats else 0)

                        if current_calls >= secret_record.limit_count:
                            return error_code.AUTH_KEY_LIMIT_EXCEEDED, ''

                    return error_code.AUTH_KEY_INVALID, ''

                return error_code.SUCCESS, secret_info

        except Exception as e:
            mcp_logger.error(f"鉴权检查失败: {str(e)}")
            return error_code.HTTP_INTERNAL_SERVER_ERROR, ''

    def _extract_auth_header(self, request: Request) -> Optional[str]:
        """从Authorization头提取密钥"""
        auth_header = request.headers.get('authorization')
        if not auth_header:
            return None

        # 支持 Bearer 格式
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # 去掉 "Bearer " 前缀

        # 支持直接传递密钥
        return auth_header

    def _extract_auth_query(self, request: Request) -> Optional[str]:
        """从查询参数提取密钥"""
        # 支持多种查询参数名称
        param_names = ['secret', 'token', 'key', 'auth']

        for param_name in param_names:
            value = request.query_params.get(param_name)
            if value:
                return value

        return None

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 优先从代理头获取真实IP
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # 取第一个IP（真实客户端IP）
            return forwarded_for.split(',')[0].strip()

        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip

        # 最后从连接信息获取
        if hasattr(request.client, 'host'):
            return request.client.host

        return 'unknown'
