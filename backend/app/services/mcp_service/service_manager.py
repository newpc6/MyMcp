"""
MCP服务管理器模块

这是动态发布MCP服务的核心功能实现，它管理多个独立的MCP服务实例，
每个实例都有自己的路由路径。用户可以为不同的模块发布单独的MCP服务，
并且可以实时启动和停止这些服务。
"""
import json
import uuid
from typing import Dict, Optional, List, Any
from starlette.routing import Route
from starlette.requests import Request
import re
import asyncio
from contextlib import AsyncExitStack

from app.core.config import settings
from app.utils.logging import mcp_logger
from app.models.engine import get_db
from backend.app.models.modules.mcp_modules import McpModule
from app.models.modules.mcp_services import McpService
from app.models.modules.users import User
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http import StreamableHTTPServerTransport
import importlib
import inspect
import os
import sys
import tempfile
from app.utils.permissions import add_edit_permission
from app.utils.http import PageParams, build_page_response


class McpServiceManager:
    """MCP服务管理器，负责启动和停止MCP服务"""

    _instance = None
    _main_app = None
    # _server = {}
    _running_services: Dict[str, Dict] = {}  # 存储正在运行的服务
    _lifespan_manager = None  # streamable http需要接入生命周期管理

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(McpServiceManager, cls).__new__(cls)
        return cls._instance

    def init_app(self, app, lifespan_manager):
        """初始化应用程序实例，保存引用"""
        self._main_app = app
        self._lifespan_manager = lifespan_manager
        # self._server = server
        self._initialize()

    def _initialize(self):
        """初始化管理器"""
        self._load_services_from_db()

    def _load_services_from_db(self):
        """从数据库中加载已存在的服务"""
        if not self._main_app:
            mcp_logger.warning("主应用程序未初始化，无法加载服务")
            return
        try:
            with get_db() as db:
                services = db.query(McpService).filter(
                    McpService.enabled == 1
                ).all()
                for service in services:
                    if not service.enabled:
                        continue
                    # 尝试重新启动已发布的服务
                    try:
                        if service.service_type == 2:  # 第三方服务
                            # 第三方服务只需要保持状态，不需要创建路由
                            mcp_logger.info(
                                f"第三方服务已加载: "
                                f"{service.service_uuid} {service.name}")
                        else:  # 内置服务
                            module = db.query(McpModule).filter(
                                McpModule.id == service.module_id
                            ).first()
                            if module:
                                # if service.protocol_type == 1:
                                #     continue
                                self._create_mcp(service, module)
                                mcp_logger.info(
                                    f"已启动mcp服务: "
                                    f"{service.service_uuid} {module.name}")
                            else:
                                mcp_logger.warning(
                                    f"服务 {service.service_uuid} "
                                    f"对应的模块不存在")
                    except Exception as e:
                        service_name = (
                            service.name if service.service_type == 2
                            else (module.name if 'module' in locals()
                                  and module else "未知")
                        )
                        msg = (f"启动mcp服务失败 {service.service_uuid} "
                               f"{service_name}: {str(e)}")
                        mcp_logger.error(msg)
                        service.status = "error"
                        service.error_message = str(e)
                        db.commit()
        except Exception as e:
            mcp_logger.error(f"启动mcp服务失败: {str(e)}")

    def _get_sse_path(self, service_uuid: str) -> str:
        """获取SSE URL"""
        return f"/mcp-{service_uuid}"

    def publish_service(self, module_id: int, user_id: Optional[int] = None,
                        is_admin: bool = False, 
                        data: Optional[Dict] = None) -> McpService:
        """发布一个MCP模块服务

        Args:
            module_id: MCP模块ID
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户
            config_params: 配置参数，包括秘钥等信息
            name: 服务名称
            protocol_type: 协议类型，1=SSE，2=流式HTTP
            sse_path: 自定义SSE路径，可选
            use_full_custom_path: 是否使用完全自定义路径，可选

        Returns:
            McpService: 创建的服务记录
        """
        name = data.get("service_name")
        config_params = data.get("config_params")
        is_public = data.get("is_public", False)
        protocol_type = data.get("protocol_type", 1)  # 默认使用SSE协议
        custom_sse_path = data.get("sse_path", "").strip()  # 获取自定义SSE路径
        use_full_custom_path = data.get("use_full_custom_path", False)

        if not self._main_app:
            raise ValueError("主应用程序未初始化，无法发布服务")

        # 检查参数
        if not name:
            raise ValueError("服务名称不能为空")

        with get_db() as db:
            # 检查模块是否存在
            module = db.query(McpModule).filter(
                McpModule.id == module_id
            ).first()
            if not module:
                raise ValueError(f"模块不存在: {module_id}")

            # 检查是否需要配置参数
            if module.config_schema:
                # 检查配置参数
                try:
                    config_schema = (
                        json.loads(module.config_schema) 
                        if isinstance(module.config_schema, str) 
                        else module.config_schema)

                    # 验证必填参数
                    for key, schema in config_schema.items():
                        if schema.get('required', False) and (
                                not config_params or key not in config_params 
                                or not config_params[key]):
                            mcp_logger.error(f"缺少必填参数: {key}")
                            raise ValueError(f"缺少必填参数: {key}")
                except json.JSONDecodeError:
                    mcp_logger.error(
                        f"config_schema解析失败: {module.config_schema}")
                    pass  # 如果解析失败则忽略

            # 检查权限: 非管理员只能发布自己创建的或公开的模块
            if not is_admin and user_id is not None:
                if not module.is_public and module.user_id != user_id:
                    raise ValueError("没有权限发布此模块")

            # 生成唯一ID
            service_uuid = str(uuid.uuid4())

            # 处理SSE路径
            if custom_sse_path:
                if use_full_custom_path:
                    # 完全自定义路径模式：直接使用用户输入的路径
                    # 确保路径以/开头
                    if not custom_sse_path.startswith('/'):
                        custom_sse_path = '/' + custom_sse_path
                    
                    # 验证自定义路径的合法性
                    import re
                    if not re.match(r'^/[a-zA-Z0-9\-_/]*$', custom_sse_path):
                        raise ValueError("自定义路径只能包含字母、数字、连字符、下划线和斜杠")
                    
                    # 检查路径是否已被占用（完全匹配）
                    existing_service = db.query(McpService).filter(
                        McpService.sse_url == custom_sse_path
                    ).first()
                    if existing_service:
                        raise ValueError(f"路径 {custom_sse_path} 已被其他服务占用")
                    
                    # 直接使用用户输入的路径
                    sse_path = custom_sse_path
                else:
                    # 标准自定义路径模式：添加/mcp前缀和协议后缀
                    # 确保路径以/开头但不以/结尾
                    if not custom_sse_path.startswith('/'):
                        custom_sse_path = '/' + custom_sse_path
                    if custom_sse_path.endswith('/'):
                        custom_sse_path = custom_sse_path.rstrip('/')
                    
                    # 验证自定义路径的合法性
                    import re
                    if not re.match(r'^/[a-zA-Z0-9\-_/]*$', custom_sse_path):
                        raise ValueError("自定义路径只能包含字母、数字、连字符、下划线和斜杠")
                    
                    # 检查路径是否已被占用（前缀匹配）
                    existing_service = db.query(McpService).filter(
                        McpService.sse_url.like(f"/mcp{custom_sse_path}%")
                    ).first()
                    if existing_service:
                        raise ValueError(f"路径 /mcp{custom_sse_path} 已被其他服务占用")
                    
                    # 构建完整的SSE路径
                    if protocol_type == 1:  # SSE协议
                        sse_path = f"/mcp{custom_sse_path}/sse"
                    elif protocol_type == 2:  # 流式HTTP协议
                        sse_path = f"/mcp{custom_sse_path}/stream"
                    else:
                        raise ValueError("不支持该协议，仅支持SSE与流式HTTP协议")
            else:
                # 使用自动生成的路径
                if protocol_type == 1:  # SSE协议
                    sse_path = f"{self._get_sse_path(service_uuid)}/sse"
                elif protocol_type == 2:  # 流式HTTP协议
                    sse_path = f"{self._get_sse_path(service_uuid)}/stream"
                else:
                    raise ValueError("不支持该协议，仅支持SSE与流式HTTP协议")

            # 处理配置参数
            params = config_params
            if isinstance(config_params, dict):
                if len(config_params) > 0:
                    params = json.dumps(config_params)
                else:
                    params = ""

            # 创建新的服务记录
            service_record = McpService(
                module_id=module_id,
                service_uuid=service_uuid,
                name=name,
                sse_url=sse_path,
                status="running",
                enabled=True,
                user_id=user_id,
                is_public=is_public,
                config_params=params,
                protocol_type=protocol_type  # 添加协议类型字段
            )
            db.add(service_record)
            db.commit()
            db.refresh(service_record)

            try:
                # 创建服务路由
                self._create_mcp(service_record, module)
                return service_record
            except Exception as e:
                service_record.status = "error"
                service_record.error_message = str(e)
                db.commit()
                mcp_logger.error(f"发布服务失败: {str(e)}")
                raise e

    def publish_third_party_service(self, user_id: Optional[int] = None,
                                    is_admin: bool = False, 
                                    data: Optional[Dict] = None) -> McpService:
        """发布一个第三方MCP服务

        Args:
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户
            data: 服务数据，包含name, sse_url, description等

        Returns:
            McpService: 创建的服务记录
        """
        if not self._main_app:
            raise ValueError("主应用程序未初始化，无法发布服务")

        # 检查参数
        name = data.get("service_name")
        sse_url = data.get("sse_url")
        description = data.get("description", "")
        is_public = data.get("is_public", False)

        if not name:
            raise ValueError("服务名称不能为空")
        if not sse_url:
            raise ValueError("SSE URL不能为空")

        # 验证URL格式
        import re
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, sse_url):
            raise ValueError("SSE URL格式不正确")

        with get_db() as db:
            # 生成唯一ID
            service_uuid = str(uuid.uuid4())

            # 创建新的服务记录
            service_record = McpService(
                module_id=None,  # 第三方服务没有模块ID
                service_uuid=service_uuid,
                name=name,
                sse_url=sse_url,  # 直接使用提供的URL
                status="stopped",  # 第三方服务默认为停止状态
                enabled=False,
                user_id=user_id,
                is_public=is_public,
                service_type=2,  # 第三方服务类型
                description=description,
                config_params=""  # 第三方服务暂不支持配置参数
            )
            db.add(service_record)
            db.commit()
            db.refresh(service_record)

            mcp_logger.info(f"成功创建第三方服务: {service_uuid} - {name}")
            return service_record

    def stop_service(self, service_uuid: str, user_id: Optional[int] = None, 
                     is_admin: bool = False) -> bool:
        """停止MCP服务

        Args:
            service_uuid: 服务UUID
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            bool: 是否成功停止
        """
        # 检查服务是否存在
        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.service_uuid == service_uuid
            ).first()
            if not service:
                return False

            # 检查权限：非管理员只能停止自己创建的服务
            if (not is_admin and user_id is not None 
                    and service.user_id != user_id):
                raise ValueError("没有权限停止此服务")

        if service_uuid not in self._running_services:
            with get_db() as db:
                service = db.query(McpService).filter(
                    McpService.service_uuid == service_uuid
                ).first()
                if not service:
                    return False
                service.status = "stopped"
                service.enabled = False
                db.commit()
            return True

        # 获取服务信息并停止服务
        service_info = self._running_services.pop(service_uuid, None)
        if service_info:
            # 如果有连接管理器，关闭它
            if "connection_manager" in service_info:
                try:
                    import asyncio
                    # 创建一个任务来异步关闭连接管理器
                    
                    async def close_connection():
                        await service_info["connection_manager"].aclose()
                    
                    # 在后台关闭连接
                    asyncio.create_task(close_connection())
                    mcp_logger.info(f"已关闭服务连接管理器: {service_uuid}")
                except Exception as e:
                    mcp_logger.error(
                        f"关闭连接管理器失败: {service_uuid}, 错误: {str(e)}"
                    )
            
            # 如果有任务，取消它们
            if "tasks" in service_info:
                for task in service_info["tasks"]:
                    if not task.done():
                        task.cancel()
                        mcp_logger.info(f"已取消服务任务: {service_uuid}")

        # 从数据库获取服务信息以获取正确的路径
        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.service_uuid == service_uuid
            ).first()
            if service:
                # 使用数据库中存储的真实路径
                sse_path = service.sse_url
                
                # 判断是否为完全自定义路径
                is_full_custom = not (sse_path.startswith('/mcp') and 
                                      (sse_path.endswith('/sse') or 
                                       sse_path.endswith('/stream')))
                
                if is_full_custom:
                    # 完全自定义路径：直接添加/messages后缀
                    message_path = f"{sse_path.rstrip('/')}/messages"
                else:
                    # 标准路径：去掉结尾的/sse或/stream，然后加上/messages
                    base_path = sse_path.rstrip('/sse').rstrip('/stream')
                    message_path = f"{base_path}/messages"

                # 删除路由
                routes_to_delete = []
                for i, route in enumerate(self._main_app.routes):
                    if hasattr(route, 'path'):
                        if route.path in [sse_path, message_path]:
                            routes_to_delete.append(route)

                # 单独删除以避免迭代时修改列表
                for route in routes_to_delete:
                    try:
                        self._main_app.routes.remove(route)
                        mcp_logger.info(f"成功删除路由: {route.path}")
                    except Exception as e:
                        mcp_logger.error(f"删除路由失败: {route.path}, 错误: {str(e)}")

                # 更新数据库状态
                service.status = "stopped"
                service.enabled = False
                db.commit()

        return True

    def start_service(self, service_uuid: str, user_id: Optional[int] = None, 
                      is_admin: bool = False) -> bool:
        """启动已停止的MCP服务

        Args:
            service_uuid: 服务UUID
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            bool: 是否成功启动
        """
        # 检查服务是否已经在运行
        if service_uuid in self._running_services:
            return True

        # 从数据库获取服务信息
        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.service_uuid == service_uuid
            ).first()
            if not service:
                return False

            # 检查权限：非管理员只能启动自己创建的服务
            if (not is_admin and user_id is not None 
                    and service.user_id != user_id):
                mcp_logger.warning(
                    f"用户 {user_id} 尝试启动非自己创建的服务 "
                    f"{service_uuid}")
                return False

            # 根据服务类型处理
            if service.service_type == 2:  # 第三方服务
                # 第三方服务只需要更新状态，不需要创建路由
                service.status = "running"
                service.error_message = ""
                service.enabled = True
                db.commit()
                db.refresh(service)
                mcp_logger.info(f"第三方服务已启动: {service_uuid} - {service.name}")
                return True
            else:  # 内置服务
                # 检查模块是否存在
                module = db.query(McpModule).filter(
                    McpModule.id == service.module_id
                ).first()
                if not module:
                    return False

                # 创建服务路由
                try:
                    self._create_mcp(service, module)
                    # 更新服务状态
                    service.status = "running"
                    service.error_message = ""
                    service.enabled = True
                    db.commit()
                    db.refresh(service)
                    return True
                except Exception as e:
                    mcp_logger.error(f"启动服务失败 {service_uuid}: {str(e)}")
                    return False

    def delete_service(self, service_uuid: str, user_id: Optional[int] = None, 
                       is_admin: bool = False) -> bool:
        """完全删除MCP服务

        Args:
            service_uuid: 服务UUID
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            bool: 是否成功删除
        """
        # 检查权限
        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.service_uuid == service_uuid
            ).first()
            if not service:
                return False

            # 检查权限：非管理员只能删除自己创建的服务
            if (not is_admin and user_id is not None 
                    and service.user_id != user_id):
                mcp_logger.warning(
                    f"用户 {user_id} 尝试删除非自己创建的服务 "
                    f"{service_uuid}")
                return False

        # 先停止服务
        self.stop_service(service_uuid, user_id, is_admin)

        # 然后从数据库删除
        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.service_uuid == service_uuid
            ).first()
            if service:
                db.delete(service)
                db.commit()
                return True

        return False

    def update_service_visibility(self, id: int, is_public: bool,
                                  user_id: Optional[int] = None, 
                                  is_admin: bool = False) -> Dict[str, Any]:
        """更新服务的公开/私有状态

        Args:
            service_uuid: 服务UUID
            is_public: 是否公开
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            Dict: 包含更新结果的字典

        Raises:
            ValueError: 当服务不存在或权限不足时
        """
        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.id == id
            ).first()

            if not service:
                raise ValueError("服务不存在")

            # 检查权限：非管理员只能修改自己创建的服务
            if (not is_admin and user_id is not None 
                    and service.user_id != user_id):
                raise ValueError("没有权限修改此服务")

            # 更新可见性状态
            service.is_public = bool(is_public)
            db.commit()

            return {
                "is_public": service.is_public,
                "id": service.id
            }

    def update_service_description(self, service_uuid: str, description: str,
                                   user_id: Optional[int] = None, 
                                   is_admin: bool = False) -> bool:
        """更新服务描述

        Args:
            service_uuid: 服务UUID
            description: 新的描述
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            bool: 是否更新成功

        Raises:
            ValueError: 当服务不存在、权限不足或模块不存在时
        """
        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.service_uuid == service_uuid
            ).first()

            if not service:
                raise ValueError("服务不存在")

            # 检查权限：非管理员只能修改自己创建的服务
            if (not is_admin and user_id is not None 
                    and service.user_id != user_id):
                raise ValueError("没有权限修改此服务")

            # 如果是第三方服务，直接更新服务的描述
            if service.service_type == 2:
                service.description = description
                db.commit()
                return True
            else:
                # 内置服务，更新关联的模块描述
                module = db.query(McpModule).filter(
                    McpModule.id == service.module_id
                ).first()

                if not module:
                    raise ValueError("未找到关联模块")

                module.description = description
                db.commit()
                return True

    def get_service_by_module_id(self, module_id: int) -> Optional[McpService]:
        """获取指定模块ID的服务

        Args:
            module_id: 模块ID
        """
        try:
            with get_db() as db:
                service = db.query(McpService).filter(
                    McpService.module_id == module_id
                ).first()
                return service
        except Exception as e:
            mcp_logger.error(f"获取指定模块ID的服务失败: {str(e)}")
            return None

    def _get_full_sse_url(self, sse_url: str, 
                          request: Optional[Request] = None) -> str:
        """获取完整的SSE URL

        如果URL已经是http://或https://开头，则直接返回，否则根据请求信息构建完整URL

        Args:
            sse_url: 原始SSE URL
            request: HTTP请求对象，用于获取主机和端口信息

        Returns:
            str: 完整的SSE URL
        """
        # 检查URL是否已经是完整的URL格式
        if sse_url and re.match(r'^(http|https)://', sse_url):
            return sse_url

        # 如果不是完整URL并且提供了请求对象，构建完整URL
        if request:
            host = request.headers.get(
                "host", f"{settings.HOST}:{settings.PORT}")
            # 前端调试模式启动情况下host为host+端口号的格式，生成的地址没问题，但是如果前端编译后用nginx代理访问
            # 拿到的host只有域名没有端口号，所以这里进行修正
            if ":" not in host:
                host = host + ":" + str(settings.PORT)
            scheme = request.headers.get("x-forwarded-proto", "http")
            return f"{scheme}://{host}{sse_url}"

        # 如果既不是完整URL也没有请求对象，返回原始URL
        return sse_url

    def get_service_status(self, service_uuid: str, 
                           request: Optional[Request] = None,
                           user_id: Optional[int] = None, 
                           is_admin: bool = False) -> Optional[Dict]:
        """获取服务状态

        Args:
            service_uuid: 服务UUID
            request: HTTP请求对象，用于构建完整URL
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            服务状态信息
        """
        # 检查是否是正在运行的服务
        service_info = self._running_services.get(service_uuid)
        if service_info:
            # 从数据库中获取服务和模块信息
            with get_db() as db:
                service = db.query(McpService).filter(
                    McpService.service_uuid == service_uuid
                ).first()
                if not service:
                    return None

                module = db.query(McpModule).filter(
                    McpModule.id == service.module_id
                ).first()
                module_name = module.name if module else "Unknown"

                # 构建服务信息
                service_data = service.to_dict()
                service_data["module_name"] = module_name
                service_data["status"] = "running"

                # 替换SSE URL为完整URL
                sse_url = service.sse_url
                service_data["sse_url"] = self._get_full_sse_url(
                    sse_url, request)

                # 添加可编辑字段
                return add_edit_permission(service_data, user_id, is_admin)
        else:
            # 如果不是运行中的服务，从数据库查询
            with get_db() as db:
                service = db.query(McpService).filter(
                    McpService.service_uuid == service_uuid
                ).first()
                if not service:
                    return None

                module = db.query(McpModule).filter(
                    McpModule.id == service.module_id
                ).first()
                module_name = module.name if module else "Unknown"

                # 构建服务信息
                service_data = service.to_dict()
                service_data["module_name"] = module_name

                # 替换SSE URL为完整URL
                sse_url = service.sse_url
                service_data["sse_url"] = self._get_full_sse_url(
                    sse_url, request)

                # 添加可编辑字段
                return add_edit_permission(service_data, user_id, is_admin)

        return None

    def list_services(self, module_id: Optional[int] = None, 
                      user_id: Optional[int] = None,
                      is_admin: bool = False, 
                      request: Optional[Request] = None) -> List[Dict]:
        """获取服务列表

        Args:
            module_id: 模块ID过滤，可选
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户
            request: HTTP请求对象，用于构建完整URL

        Returns:
            服务列表
        """
        with get_db() as db:
            # 构建主查询，联表查询用户和模块信息
            query = db.query(McpService).outerjoin(
                McpModule, McpService.module_id == McpModule.id
            ).outerjoin(
                User, McpService.user_id == User.id
            )

            # 如果指定了模块ID，按模块过滤
            if module_id:
                query = query.filter(McpService.module_id == module_id)

            # 权限控制：非管理员只能看到自己的服务或公开的服务，管理员可以看到所有服务
            if not is_admin and user_id is not None:
                # 非管理员只能搜索公开服务或自己的服务
                # 对于有模块的服务，需要同时检查服务和模块的公开状态
                # 对于第三方服务（module_id为NULL），只检查服务的公开状态
                public_filter = (
                    (McpService.is_public.is_(True)) &
                    ((McpService.module_id.is_(None))
                     | (McpModule.is_public.is_(True)))
                )
                own_filter = (McpService.user_id == user_id)
                query = query.filter(public_filter | own_filter)
            elif is_admin:
                pass
            else:
                # 未登录用户只能看到公开的服务
                # 对于有模块的服务，需要同时检查服务和模块的公开状态
                # 对于第三方服务（module_id为NULL），只检查服务的公开状态
                query = query.filter(
                    (McpService.is_public.is_(True)) &
                    ((McpService.module_id.is_(None))
                     | (McpModule.is_public.is_(True)))
                )

            services = query.all()
            
            # 批量获取模块和用户信息，避免在循环中重复查询
            module_ids = [s.module_id for s in services if s.module_id]
            user_ids = [s.user_id for s in services if s.user_id]
            
            # 批量查询模块信息
            module_info = {}
            if module_ids:
                modules = db.query(McpModule).filter(
                    McpModule.id.in_(module_ids)
                ).all()
                module_info = {
                    m.id: {'name': m.name, 'description': m.description} 
                    for m in modules
                }
            
            # 批量查询用户信息
            user_info = {}
            if user_ids:
                users = db.query(User).filter(
                    User.id.in_(user_ids)
                ).all()
                user_info = {
                    u.id: {'username': u.username} 
                    for u in users
                }
            
            result = []

            # 获取每个服务的详细信息
            for service in services:
                service_dict = service.to_dict(module_info, user_info)

                # 处理模块描述信息
                if service.module_id and service.module_id in module_info:
                    # 内置服务，从模块获取描述
                    service_dict["description"] = (
                        module_info[service.module_id]['description'] or ""
                    )
                else:
                    # 第三方服务，使用服务本身的描述
                    service_dict["description"] = service.description or ""

                # 替换SSE URL为完整URL
                sse_url = service.sse_url
                service_dict["sse_url"] = self._get_full_sse_url(
                    sse_url, request)

                # 检查服务是否正在运行
                running_info = self._running_services.get(service.service_uuid)
                if running_info:
                    service_dict["status"] = "running"

                result.append(service_dict)

            # 添加可编辑字段
            return add_edit_permission(result, user_id, is_admin)

    def page_services(
            self,
            page_params: PageParams,
            user_id: Optional[int] = None,
            is_admin: bool = False,
            condition: Optional[Dict] = None,
            request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """获取服务列表（分页）

        Args:
            page_params: 分页参数
            module_id: 模块ID过滤，可选
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户
            request: HTTP请求对象，用于构建完整URL
            search_name: 搜索服务名称
            search_status: 搜索服务状态
            search_user_id: 搜索用户ID

        Returns:
            分页结果字典
        """
        with get_db() as db:
            # 构建主查询，联表查询用户和模块信息
            query = db.query(McpService).outerjoin(
                McpModule, McpService.module_id == McpModule.id
            ).outerjoin(
                User, McpService.user_id == User.id
            )

            # 如果指定了模块ID，按模块过滤
            if condition.get("module_id"):
                query = query.filter(McpService.module_id ==
                                     condition.get("module_id"))

            # 权限控制：非管理员只能看到自己的服务或公开的服务，管理员可以看到所有服务
            if not is_admin and user_id is not None:
                # 非管理员只能搜索公开服务或自己的服务
                # 对于有模块的服务，需要同时检查服务和模块的公开状态
                # 对于第三方服务（module_id为NULL），只检查服务的公开状态
                public_filter = (
                    (McpService.is_public.is_(True)) &
                    ((McpService.module_id.is_(None))
                     | (McpModule.is_public.is_(True)))
                )
                own_filter = (McpService.user_id == user_id)
                query = query.filter(public_filter | own_filter)
            elif not is_admin:
                # 未登录用户只能看到公开的服务
                # 对于有模块的服务，需要同时检查服务和模块的公开状态
                # 对于第三方服务（module_id为NULL），只检查服务的公开状态
                query = query.filter(
                    (McpService.is_public.is_(True)) &
                    ((McpService.module_id.is_(None))
                     | (McpModule.is_public.is_(True)))
                )

            # 搜索条件
            if condition.get("name"):
                query = query.filter(
                    McpService.name.like(f'%{condition.get("name")}%')
                )

            if condition.get("status"):
                query = query.filter(McpService.status ==
                                     condition.get("status"))

            if condition.get("user_id"):
                query = query.filter(
                    User.id == condition.get("user_id")
                )

            # 获取总数
            total_count = query.count()

            # 分页查询，按创建时间倒序
            services = query.order_by(McpService.created_at.desc()).offset(
                page_params.offset
            ).limit(page_params.size).all()

            # 批量获取模块和用户信息，避免在循环中重复查询
            module_ids = [s.module_id for s in services if s.module_id]
            user_ids = [s.user_id for s in services if s.user_id]
            
            # 批量查询模块信息
            module_info = {}
            if module_ids:
                modules = db.query(McpModule).filter(
                    McpModule.id.in_(module_ids)
                ).all()
                module_info = {
                    m.id: {'name': m.name, 'description': m.description} 
                    for m in modules
                }
            
            # 批量查询用户信息
            user_info = {}
            if user_ids:
                users = db.query(User).filter(
                    User.id.in_(user_ids)
                ).all()
                user_info = {
                    u.id: {'username': u.username} 
                    for u in users
                }

            result_items = []

            # 获取每个服务的详细信息
            for service in services:
                service_dict = service.to_dict(module_info, user_info)

                # 处理模块描述信息
                if service.module_id and service.module_id in module_info:
                    # 内置服务，从模块获取描述
                    service_dict["description"] = (
                        module_info[service.module_id]['description'] or ""
                    )
                else:
                    # 第三方服务，使用服务本身的描述
                    service_dict["description"] = service.description or ""

                # 替换SSE URL为完整URL
                sse_url = service.sse_url
                service_dict["sse_url"] = self._get_full_sse_url(
                    sse_url, request
                )

                # 检查服务是否正在运行
                running_info = self._running_services.get(
                    service.service_uuid
                )
                if running_info:
                    service_dict["status"] = "running"

                result_items.append(service_dict)

            # 添加可编辑字段
            result_items = add_edit_permission(
                result_items, user_id, is_admin
            )

            return build_page_response(
                result_items,
                total_count,
                page_params
            )

    def replace_config_params(self, code: str, config_params: Dict) -> str:
        """替换配置参数

        Args:
            code: 代码
            config_params: 配置参数
        """
        for key, value in config_params.items():
            # 使用统一的替换标记格式 "${参数名}"
            placeholder = "${" + key + "}"

            # 根据值类型进行不同的替换
            if isinstance(value, str):
                # 字符串类型需要添加引号
                code = code.replace(placeholder, f'"{value}"')
            else:
                # 数字、布尔等类型不需要引号
                code = code.replace(placeholder, str(value))
        return code

    def register_mcp_tool(self, service_uuid: str, service: McpService, 
                          module: McpModule):
        """注册指定服务UUID对应模块的工具函数

        Args:
            service_uuid: 服务UUID，用于找到对应的模块并注册其工具
        """
        if not service_uuid or service_uuid not in self._running_services:
            mcp_logger.error(f"无效的服务UUID: {service_uuid}")
            return

        try:
            code = module.code
            if service.config_params and module.code:
                config_params = None
                if isinstance(service.config_params, str):
                    config_params = json.loads(service.config_params)
                else:
                    config_params = service.config_params
                code = self.replace_config_params(code, config_params)
            # 在数据库会话内复制需要的数据，而不是直接使用数据库对象
            module_name = module.name
            module_code = code

            # 数据库会话结束后，使用复制的数据而不是数据库对象
            mcp_logger.info(f"为服务 {service_uuid} 加载模块: {module_name}")

            # 创建临时目录存放代码文件
            temp_dir = tempfile.mkdtemp(
                prefix=f"mcp_module_{service_uuid}_")

            # 添加临时目录到Python路径
            if temp_dir not in sys.path:
                sys.path.insert(0, temp_dir)

            # 创建临时模块文件
            module_filename = f"{module_name}.py"
            module_path = os.path.join(temp_dir, module_filename)

            # 将代码写入临时文件
            with open(module_path, "w", encoding="utf-8") as f:
                f.write(module_code)

            # 动态导入模块
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            if spec and spec.loader:
                module_obj = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module_obj)
                mcp_logger.info(f"成功导入模块: {module_name}")

                # 遍历模块中的所有函数
                for name, func in inspect.getmembers(
                        module_obj, inspect.isfunction):
                    if name.startswith("_"):
                        # 过滤掉以_开头的函数
                        continue
                    # 过滤出该模块定义的函数(而不是导入的函数)
                    if func.__module__ == module_name:
                        # 获取函数文档
                        doc = inspect.getdoc(func)

                        # 将工具注册到对应的服务实例
                        server = self._running_services[service_uuid]["server"]
                        server.add_tool(func, name=name, description=doc)
                        mcp_logger.info(
                            f"为服务 {service_uuid} 注册工具: {name}")

        except Exception as e:
            mcp_logger.error(f"为服务 {service_uuid} 注册工具失败: {str(e)}")

    def _create_mcp(self, service: McpService, module: McpModule):
        """创建MCP服务实例"""
        service_uuid = service.service_uuid

        try:
            if not module.code:
                mcp_logger.warning(f"模块 {module.name} 没有代码内容，跳过")
                service.status = "error"
                service.error_message = "模块没有代码内容"
                with get_db() as db:
                    db_service = db.query(McpService).filter(
                        McpService.service_uuid == service_uuid
                    ).first()
                    if db_service:
                        db_service.status = "error"
                        db_service.error_message = "模块没有代码内容"
                        db.commit()
                raise ValueError("模块没有代码内容")

            if self._running_services.get(service.service_uuid):
                mcp_logger.info(f"服务 {service.service_uuid} 已存在，不重复创建")
                raise ValueError("服务已存在，不重复创建")

            if not self._main_app:
                service.status = "error"
                service.error_message = "主应用程序未初始化，无法创建路由"
                with get_db() as db:
                    db_service = db.query(McpService).filter(
                        McpService.service_uuid == service_uuid
                    ).first()
                    if db_service:
                        db_service.status = "error"
                        db_service.error_message = "主应用程序未初始化，无法创建路由"
                        db.commit()
                raise ValueError("主应用程序未初始化，无法创建路由")

            # 在数据库会话外复制需要的模块信息
            module_name = module.name
            service_uuid = service.service_uuid

            # 为每个服务创建独立的FastMCP实例，而不是使用共享实例
            self._running_services[service_uuid] = {
                "server": FastMCP(
                    name=f"{module_name} MCP Server",
                    host=settings.HOST,
                    port=settings.PORT,
                ),
                "routes": []
            }
            self.register_mcp_tool(service_uuid, service, module)

            # 根据不同的协议类型，创建相应的路由
            if service.protocol_type == 1:  # SSE协议
                self._create_sse_handlers(service)
            elif service.protocol_type == 2:  # 流式HTTP协议
                self._create_stream_handlers(service)

        except Exception as e:
            mcp_logger.error(f"创建MCP服务失败: {str(e)}")
            # 更新服务状态为错误
            with get_db() as db:
                service_record = db.query(McpService).filter(
                    McpService.service_uuid == service_uuid
                ).first()
                if service_record:
                    service_record.status = "error"
                    service_record.error_message = str(e)
                    db.commit()
            raise e

    def _create_sse_handlers(self, service: McpService):
        """创建SSE协议相关的处理函数和路由"""
        service_uuid = service.service_uuid

        # 直接使用数据库中存储的sse_url路径
        sse_path = service.sse_url
        
        # 判断是否为完全自定义路径（不包含/mcp前缀和/sse后缀）
        is_full_custom = not (sse_path.startswith('/mcp') and 
                              (sse_path.endswith('/sse') or 
                               sse_path.endswith('/stream')))
        
        if is_full_custom:
            # 完全自定义路径：直接添加/messages后缀
            message_path = f"{sse_path.rstrip('/')}/messages/"
        else:
            # 标准路径：去掉结尾的/sse或/stream，然后加上/messages/
            base_path = sse_path.rstrip('/sse').rstrip('/stream')
            message_path = f"{base_path}/messages/"

        # 创建SSE应用
        sse = SseServerTransport(message_path)
        # 删除现有路由（如果存在）
        routes_to_delete = []
        for i, route in enumerate(self._main_app.routes):
            if hasattr(route, 'path'):
                if route.path == sse_path:
                    routes_to_delete.append(route)
                if route.path == message_path:
                    routes_to_delete.append(route)

        # 单独删除以避免迭代时修改列表
        for route in routes_to_delete:
            try:
                self._main_app.routes.remove(route)
                mcp_logger.info(f"已删除现有路由: {route.path}")
            except Exception as e:
                mcp_logger.error(f"删除路由失败: {route.path}, 错误: {str(e)}")

        # 创建SSE处理函数，使用特定服务的server实例
        mcp_server = self._running_services[service_uuid]["server"]._mcp_server

        async def handle_sse(request: Request) -> None:
            try:
                mcp_logger.info(f"开始处理SSE请求: service_uuid={service_uuid}")
                async with sse.connect_sse(
                        request.scope,
                        request.receive,
                        request._send,
                ) as streams:
                    if self._running_services.get(service_uuid):
                        mcp_logger.info(f"开始运行服务 {service_uuid} 的MCP服务器")
                        await mcp_server.run(
                            streams[0],
                            streams[1],
                            mcp_server.create_initialization_options(
                            ),
                        )
                    else:
                        mcp_logger.error(f"服务 {service_uuid} 不存在或已停止")
            except Exception as e:
                mcp_logger.error(
                    f"处理SSE请求失败: service_uuid={service_uuid}, 错误: {str(e)}")
            finally:
                mcp_logger.info(f"SSE连接关闭: service_uuid={service_uuid}")

        # 添加服务路由到主应用
        route = Route(
            path=sse_path,
            endpoint=handle_sse,
            methods=None,
            name=None,
            include_in_schema=True,
        )
        # 在所有路由之前插入，不然会被spa路由捕获
        self._main_app.routes.insert(0, route)
        self._main_app.mount(message_path, sse.handle_post_message)
        with get_db() as db:
            service_db = db.query(McpService).filter(
                McpService.service_uuid == service.service_uuid
            ).first()
            if service_db:
                service_db.status = "running"
                service_db.error_message = ""
                db.commit()

    def _create_stream_handlers(self, service: McpService):
        """创建流式HTTP协议相关的处理函数和路由"""
        service_uuid = service.service_uuid

        # 直接使用数据库中存储的sse_url路径
        streamable_http_path = service.sse_url
        
        # 删除现有路由（如果存在）
        routes_to_delete = []
        for route in self._main_app.routes:
            if hasattr(route, 'path') and route.path == streamable_http_path:
                routes_to_delete.append(route)

        # 单独删除以避免迭代时修改列表
        for route in routes_to_delete:
            try:
                self._main_app.routes.remove(route)
                mcp_logger.info(f"已删除现有路由: {route.path}")
            except Exception as e:
                mcp_logger.error(f"删除路由失败: {route.path}, 错误: {str(e)}")

        # 创建StreamableHTTPServerTransport实例
        streamable_http_transport = StreamableHTTPServerTransport(
            mcp_session_id=service_uuid,  # 使用service_uuid作为session_id
            is_json_response_enabled=False,  # 使用SSE响应模式
            event_store=None  # 暂不使用事件存储
        )

        mcp_server = self._running_services[service_uuid]["server"]._mcp_server

        # 创建连接管理器
        connection_manager = AsyncExitStack()
        connection_ready = asyncio.Event()
        
        async def setup_connection():
            """设置并维持MCP连接"""
            try:
                mcp_logger.info(f"启动流式HTTP MCP连接: {service_uuid}")
                # 建立连接
                context_manager = streamable_http_transport.connect()
                streams = await connection_manager.enter_async_context(
                    context_manager
                )
                read_stream, write_stream = streams
                
                # 标记连接已准备好
                connection_ready.set()
                
                # 运行MCP服务器
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
            except Exception as e:
                mcp_logger.error(
                    f"流式HTTP MCP连接失败: {service_uuid}, 错误: {str(e)}"
                )
                # 更新服务状态为错误
                with get_db() as db:
                    service_db = db.query(McpService).filter(
                        McpService.service_uuid == service_uuid
                    ).first()
                    if service_db:
                        service_db.status = "error"
                        service_db.error_message = str(e)
                        db.commit()
                raise
            finally:
                await connection_manager.aclose()

        # 启动连接任务
        try:
            # 获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，创建新任务
                connection_task = loop.create_task(setup_connection())
            else:
                # 如果事件循环未运行，创建新的事件循环并在后台运行任务
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                def run_in_background():
                    """在后台运行连接任务"""
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(setup_connection())
                
                # 在线程中运行连接任务
                import threading
                thread = threading.Thread(target=run_in_background)
                thread.daemon = True
                thread.start()
                connection_task = None
        except Exception as e:
            mcp_logger.error(f"启动流式HTTP连接失败: {service_uuid}, 错误: {str(e)}")
            connection_task = None

        # 创建路由处理函数
        async def handle_streamable_http(request: Request):
            """处理流式HTTP请求"""
            try:
                mcp_logger.info(f"处理流式HTTP请求: {service_uuid}")
                # 等待连接准备就绪
                await connection_ready.wait()
                
                # 创建响应流
                from starlette.responses import StreamingResponse
                import asyncio
                
                # 创建队列来收集响应数据
                response_queue = asyncio.Queue()
                response_headers = {}
                response_status = 200
                
                async def custom_send(message):
                    """自定义发送函数来捕获响应"""
                    nonlocal response_headers, response_status
                    if message['type'] == 'http.response.start':
                        response_status = message['status']
                        response_headers = dict(message.get('headers', []))
                    elif message['type'] == 'http.response.body':
                        await response_queue.put(message.get('body', b''))
                        if not message.get('more_body', False):
                            await response_queue.put(None)  # 结束标记
                
                # 创建后台任务处理transport请求
                async def handle_transport():
                    try:
                        await streamable_http_transport.handle_request(
                            request.scope, request.receive, custom_send
                        )
                    except Exception as e:
                        mcp_logger.error(f"Transport处理失败: {e}")
                        await response_queue.put(None)
                
                # 启动transport处理任务
                transport_task = asyncio.create_task(handle_transport())
                
                async def generate_response():
                    """生成响应数据"""
                    try:
                        while True:
                            chunk = await response_queue.get()
                            if chunk is None:
                                break
                            yield chunk
                    finally:
                        if not transport_task.done():
                            transport_task.cancel()
                
                # 返回流式响应
                return StreamingResponse(
                    generate_response(),
                    status_code=response_status,
                    headers=response_headers
                )
                
            except Exception as e:
                mcp_logger.error(
                    f"处理流式HTTP请求失败: {service_uuid}, 错误: {str(e)}"
                )
                from starlette.responses import PlainTextResponse
                return PlainTextResponse(
                    f"流式HTTP处理失败: {str(e)}", status_code=500
                )

        # 使用Route方式直接注册路由
        from starlette.routing import Route
        route = Route(
            path=streamable_http_path,
            endpoint=handle_streamable_http,
            methods=["GET", "POST", "OPTIONS"],
            name=f"mcp_stream_{service_uuid}",
            include_in_schema=True,
        )

        # 在所有路由之前插入，防止被SPA路由捕获
        mcp_logger.info(
            f"插入流式HTTP路由前，当前路由数量: {len(self._main_app.routes)}"
        )
        
        # 直接插入到最前面，与SSE路由相同的处理方式
        self._main_app.routes.insert(0, route)
        mcp_logger.info(f"流式HTTP路由已插入到位置0: {streamable_http_path}")
        
        # 验证路由是否正确注册
        route_found = False
        for i, existing_route in enumerate(self._main_app.routes):
            if (hasattr(existing_route, 'path') and
                    existing_route.path == streamable_http_path):
                route_found = True
                mcp_logger.info(
                    f"确认流式HTTP路由已注册在位置 {i}: "
                    f"{existing_route.path}"
                )
                break
        
        if not route_found:
            mcp_logger.error(
                f"流式HTTP路由注册失败: {streamable_http_path}"
            )
            raise RuntimeError(
                f"流式HTTP路由注册失败: {streamable_http_path}"
            )
        
        # 将任务和连接管理器保存到运行服务中，以便后续清理
        if "tasks" not in self._running_services[service_uuid]:
            self._running_services[service_uuid]["tasks"] = []
        if connection_task:
            self._running_services[service_uuid]["tasks"].append(
                connection_task
            )
        
        # 保存transport实例和连接管理器以便后续使用
        running_service = self._running_services[service_uuid]
        running_service["transport"] = streamable_http_transport
        running_service["connection_manager"] = connection_manager
        running_service["connection_ready"] = connection_ready

        # 更新数据库状态
        with get_db() as db:
            service_db = db.query(McpService).filter(
                McpService.service_uuid == service.service_uuid
            ).first()
            if service_db:
                service_db.status = "running"
                service_db.error_message = ""
                db.commit()

        mcp_logger.info(
            f"流式HTTP服务已启动: {service_uuid} at {streamable_http_path}"
        )

    def _remove_service_routes(self, service_uuid: str):
        """移除服务路由

        Args:
            service_uuid: 服务UUID
        """
        if not self._main_app:
            return

        # 移除路由（如果存在）
        routes_to_remove = [
            f"/api/mcp/{service_uuid}/sse",
            f"/api/mcp/{service_uuid}/messages"
            f"/api/mcp/{service_uuid}/stream"
        ]

        for route in list(self._main_app.routes):
            if hasattr(route, 'path') and route.path in routes_to_remove:
                mcp_logger.info(f"移除路由: {route.path}")
                self._main_app.routes.remove(route)

    def get_modules_for_select(self, user_id: Optional[int] = None, 
                               is_admin: bool = False) -> List[Dict[str, Any]]:
        """获取模块列表用于下拉选择器

        Args:
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            List[Dict]: 模块列表
        """
        with get_db() as db:
            # 构建查询
            query = db.query(McpModule)

            # 权限控制：非管理员只能看到公开模块或自己创建的模块
            if not is_admin and user_id is not None:
                query = query.filter(
                    (McpModule.is_public.is_(True)) |
                    (McpModule.user_id == user_id)
                )
            elif not is_admin:
                # 未登录用户只能看到公开模块
                query = query.filter(McpModule.is_public.is_(True))

            modules = query.order_by(McpModule.name).all()

            # 转换为简单的选项格式
            return [
                {
                    "id": module.id,
                    "name": module.name,
                    "description": module.description or ""
                }
                for module in modules
            ]

    def get_users_for_select(self, user_id: Optional[int] = None, 
                             is_admin: bool = False) -> List[Dict[str, Any]]:
        """获取用户列表用于下拉选择器

        Args:
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            List[Dict]: 用户列表

        Raises:
            ValueError: 当权限不足时
        """
        # 只有管理员可以查看所有用户列表
        if not is_admin:
            raise ValueError("权限不足")

        with get_db() as db:
            users = db.query(User).order_by(User.username).all()

            # 转换为简单的选项格式
            return [
                {
                    "id": user.id,
                    "name": user.username,
                    "is_admin": getattr(user, 'is_admin', False)
                }
                for user in users
            ]


# 创建全局实例
service_manager = McpServiceManager()
