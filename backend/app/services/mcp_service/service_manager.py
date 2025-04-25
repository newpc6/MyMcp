"""
MCP服务管理器模块

这是动态发布MCP服务的核心功能实现，它管理多个独立的MCP服务实例，
每个实例都有自己的路由路径。用户可以为不同的模块发布单独的MCP服务，
并且可以实时启动和停止这些服务。
"""
import json
import uuid
import threading
import time
from typing import Dict, Optional, List, Callable
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
from starlette.requests import Request

from app.core.config import settings
from app.utils.logging import em_logger
from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpModule
from app.models.modules.mcp_services import McpService
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
import importlib
import inspect
import os
import sys
import tempfile
from sqlalchemy import select


class McpServiceManager:
    """MCP服务管理器，负责启动和停止MCP服务"""

    _instance = None
    _main_app = None
    # _server = {}
    _running_services: Dict[str, Dict] = {}  # 存储正在运行的服务

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(McpServiceManager, cls).__new__(cls)
        return cls._instance

    def init_app(self, app):
        """初始化应用程序实例，保存引用"""
        self._main_app = app
        # self._server = server
        self._initialize()

    def _initialize(self):
        """初始化管理器"""
        self._load_services_from_db()

    def _load_services_from_db(self):
        """从数据库中加载已存在的服务"""
        if not self._main_app:
            em_logger.warning("主应用程序未初始化，无法加载服务")
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
                        module = db.query(McpModule).filter(
                            McpModule.id == service.module_id
                        ).first()
                        if module:
                            self._create_mcp(service, module)
                            em_logger.info(
                                f"已启动mcp服务: {service.service_uuid} {module.name}")
                    except Exception as e:
                        msg = f"启动mcp服务失败 {service.service_uuid} {module.name}: {str(e)}"
                        em_logger.error(msg)
                        service.status = "error"
                        db.commit()
        except Exception as e:
            em_logger.error(f"启动mcp服务失败: {str(e)}")

    def _get_sse_path(self, service_uuid: str) -> str:
        """获取SSE URL"""
        return f"/mcp-{service_uuid}"

    def publish_service(self, module_id: int, user_id: Optional[int] = None, is_admin: bool = False, config_params: Optional[Dict] = None) -> McpService:
        """发布一个MCP模块服务

        Args:
            module_id: MCP模块ID
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户
            config_params: 配置参数，包括秘钥等信息

        Returns:
            McpService: 创建的服务记录
        """
        if not self._main_app:
            raise ValueError("主应用程序未初始化，无法发布服务")

        # 检查是否已经发布
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
                    import json
                    config_schema = json.loads(module.config_schema) if isinstance(module.config_schema, str) else module.config_schema
                    
                    # 验证必填参数
                    for key, schema in config_schema.items():
                        if schema.get('required', False) and (not config_params or key not in config_params or not config_params[key]):
                            raise ValueError(f"缺少必填参数: {key}")
                except json.JSONDecodeError:
                    em_logger.error(f"config_schema解析失败: {module.config_schema}")
                    pass  # 如果解析失败则忽略

            # 检查权限: 非管理员只能发布自己创建的或公开的模块
            if not is_admin and user_id is not None:
                if not module.is_public and module.user_id != user_id:
                    raise ValueError("没有权限发布此模块")

            # 检查用户是否已发布此模块的服务
            query = db.query(McpService).filter(
                McpService.module_id == module_id
            )
            if user_id is not None:
                query = query.filter(McpService.user_id == user_id)
            existing = query.first()
            if existing and existing.status == "running":
                # 对于已发布的服务，检查是否为同一用户或管理员
                if not is_admin and user_id is not None and existing.user_id != user_id:
                    raise ValueError(f"此模块已被其他用户发布服务")
                raise ValueError(f"模块 {module_id} 已经发布服务")

            # 生成唯一ID
            service_uuid = str(
                uuid.uuid4()) if not existing else existing.service_uuid

            # 构建SSE URL
            sse_url = f"{settings.SSE_SERVER_URL}{self._get_sse_path(service_uuid)}/sse"

            if existing:
                # 检查是否为同一用户或管理员
                if not is_admin and user_id is not None and existing.user_id != user_id:
                    raise ValueError("没有权限更新此服务")

                # 更新现有服务
                existing.sse_url = sse_url
                existing.status = "running"
                existing.config_params = config_params
                service_record = existing
            else:
                # 创建新的服务记录
                service_record = McpService(
                    module_id=module_id,
                    service_uuid=service_uuid,
                    sse_url=sse_url,
                    status="running",
                    enabled=True,
                    user_id=user_id,
                    config_params=json.dumps(config_params) if isinstance(config_params, dict) else config_params
                )
                db.add(service_record)

            db.commit()
            db.refresh(service_record)

            # 创建服务路由
            self._create_mcp(service_record, module)

            return service_record

    def stop_service(self, service_uuid: str, user_id: Optional[int] = None, is_admin: bool = False) -> bool:
        """停止MCP服务

        Args:
            service_uuid: 服务UUID
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            bool: 是否成功停止
        """
        try:
            # 检查服务是否存在
            with get_db() as db:
                service = db.query(McpService).filter(
                    McpService.service_uuid == service_uuid
                ).first()
                if not service:
                    return False

                # 检查权限：非管理员只能停止自己创建的服务
                if not is_admin and user_id is not None and service.user_id != user_id:
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
            self._running_services.pop(service_uuid, None)
            # 添加服务路由到主应用
            sse_path = f"{self._get_sse_path(service_uuid)}/sse"
            message_path = f"{self._get_sse_path(service_uuid)}/messages"

            # 删除路由
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
                    em_logger.info(f"成功删除路由: {route.path}")
                except Exception as e:
                    em_logger.error(f"删除路由失败: {route.path}, 错误: {str(e)}")

            # 更新数据库状态
            with get_db() as db:
                service = db.query(McpService).filter(
                    McpService.service_uuid == service_uuid
                ).first()
                if service:
                    service.status = "stopped"
                    service.enabled = False
                    db.commit()

            return True
        except Exception as e:
            em_logger.error(f"停止服务失败 {service_uuid}: {str(e)}")
            return False

    def start_service(self, service_uuid: str, user_id: Optional[int] = None, is_admin: bool = False) -> bool:
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
            if not is_admin and user_id is not None and service.user_id != user_id:
                em_logger.warning(f"用户 {user_id} 尝试启动非自己创建的服务 {service_uuid}")
                return False

            # 检查模块是否存在
            module = db.query(McpModule).filter(
                McpModule.id == service.module_id
            ).first()
            if not module:
                return False

            # 更新服务状态
            service.status = "running"
            service.enabled = True
            db.commit()
            db.refresh(service)
            # 创建服务路由
            try:
                self._create_mcp(service, module)
                return True
            except Exception as e:
                em_logger.error(f"启动服务失败 {service_uuid}: {str(e)}")
                # 如果启动失败，更新状态为错误
                with get_db() as db:
                    service = db.query(McpService).filter(
                        McpService.service_uuid == service_uuid
                    ).first()
                    if service:
                        service.status = "error"
                        db.commit()
                return False

    def delete_service(self, service_uuid: str, user_id: Optional[int] = None, is_admin: bool = False) -> bool:
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
            if not is_admin and user_id is not None and service.user_id != user_id:
                em_logger.warning(f"用户 {user_id} 尝试删除非自己创建的服务 {service_uuid}")
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

    def get_service_status(self, service_uuid: str) -> Optional[Dict]:
        """获取服务状态

        Args:
            service_uuid: 服务UUID

        Returns:
            Dict: 服务状态信息
        """
        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.service_uuid == service_uuid
            ).first()
            if not service:
                return None

            # 获取模块名称和描述
            module = db.query(McpModule).filter(
                McpModule.id == service.module_id
            ).first()
            module_name = module.name if module else None
            module_description = module.description if module else ""

            # 转换为字典
            return {
                "id": service.id,
                "module_id": service.module_id,
                "module_name": module_name,
                "description": module_description,
                "service_uuid": service.service_uuid,
                "status": service.status,
                "sse_url": service.sse_url,
                "created_at": service.created_at.isoformat()
                if service.created_at else None,
                "updated_at": service.updated_at.isoformat()
                if service.updated_at else None
            }

    def list_services(self, module_id: Optional[int] = None, user_id: Optional[int] = None, is_admin: bool = False) -> List[Dict]:
        """列出所有服务

        Args:
            module_id: 可选的模块ID筛选
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户

        Returns:
            List[Dict]: 服务列表
        """
        with get_db() as db:
            query = db.query(McpService)
            if module_id is not None:
                query = query.filter(McpService.module_id == module_id)

            # 非管理员只能看到自己创建的服务
            if not is_admin and user_id is not None:
                query = query.filter(McpService.user_id == user_id)

            services = query.all()

            # 获取所有使用的模块ID
            module_ids = [service.module_id for service in services]

            # 批量查询模块信息
            modules_map = {}
            modules_description_map = {}
            if module_ids:
                modules = db.query(McpModule).filter(
                    McpModule.id.in_(module_ids)
                ).all()
                modules_map = {m.id: m.name for m in modules}
                modules_description_map = {
                    m.id: m.description for m in modules}

            return [
                {
                    "id": service.id,
                    "module_id": service.module_id,
                    "module_name": modules_map.get(service.module_id),
                    "description": modules_description_map.get(service.module_id, ""),
                    "service_uuid": service.service_uuid,
                    "status": service.status,
                    "sse_url": service.sse_url,
                    "user_id": service.user_id,
                    "user_name": service.get_user_name(),
                    "created_at": service.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    if service.created_at else None,
                    "updated_at": service.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    if service.updated_at else None
                }
                for service in services
            ]

    def register_mcp_tool(self, service_uuid: str):
        """注册指定服务UUID对应模块的工具函数

        Args:
            service_uuid: 服务UUID，用于找到对应的模块并注册其工具
        """
        if not service_uuid or service_uuid not in self._running_services:
            em_logger.error(f"无效的服务UUID: {service_uuid}")
            return

        try:
            # 从数据库获取指定服务对应的模块
            with get_db() as db:
                # 先获取服务信息
                service = db.query(McpService).filter(
                    McpService.service_uuid == service_uuid
                ).first()

                if not service:
                    em_logger.error(f"未找到服务: {service_uuid}")
                    return

                # 获取对应的模块
                module = db.query(McpModule).filter(
                    McpModule.id == service.module_id
                ).first()

                if not module:
                    em_logger.error(f"未找到模块: ID={service.module_id}")
                    return

                if not module.code:
                    em_logger.warning(f"模块 {module.name} 没有代码内容，跳过")
                    return

                # 在数据库会话内复制需要的数据，而不是直接使用数据库对象
                module_name = module.name
                module_code = module.code

            # 数据库会话结束后，使用复制的数据而不是数据库对象
            em_logger.info(f"为服务 {service_uuid} 加载模块: {module_name}")

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
                em_logger.info(f"成功导入模块: {module_name}")

                # 遍历模块中的所有函数
                for name, func in inspect.getmembers(
                        module_obj, inspect.isfunction):
                    # 过滤出该模块定义的函数(而不是导入的函数)
                    if func.__module__ == module_name:
                        # 获取函数文档
                        doc = inspect.getdoc(func)

                        # 将工具注册到对应的服务实例
                        self._running_services[service_uuid]["server"].add_tool(
                            func, name=name, description=doc)
                        em_logger.info(
                            f"为服务 {service_uuid} 注册工具: {name}")

        except Exception as e:
            em_logger.error(f"为服务 {service_uuid} 注册工具失败: {str(e)}")

    def _create_mcp(self, service: McpService, module: McpModule):
        """创建MCP服务实例"""
        service_uuid = service.service_uuid

        try:
            # 为MCP服务创建一个临时模块文件
            code = module.code
            
            # 如果有配置参数，替换代码中的变量
            if service.config_params and code:
                config_params = None
                if isinstance(service.config_params, str):
                    config_params = json.loads(service.config_params)
                else:
                    config_params = service.config_params
                # 处理配置参数替换
                for key, value in config_params.items():
                    # 构建可能的变量格式
                    var_patterns = [
                        f'"{key}" = "REPLACE_ME"',
                        f'"{key}"="REPLACE_ME"',
                        f"'{key}' = 'REPLACE_ME'",
                        f"'{key}'='REPLACE_ME'",
                        f'{key} = "REPLACE_ME"',
                        f"{key} = 'REPLACE_ME'",
                        f'{key}="REPLACE_ME"',
                        f"{key}='REPLACE_ME'"
                    ]
                    
                    # 为每种模式尝试替换
                    for pattern in var_patterns:
                        # 替换为带引号的值
                        if isinstance(value, str):
                            replace_value = f'"{key}" = "{value}"'
                            code = code.replace(pattern, replace_value)
                            
                            # 无引号变量名格式
                            no_quotes_pattern = f"{key} = \"REPLACE_ME\""
                            no_quotes_replace = f"{key} = \"{value}\""
                            code = code.replace(no_quotes_pattern, no_quotes_replace)
                        else:
                            # 对于非字符串值，直接插入无引号
                            replace_value = f'"{key}" = {value}'
                            code = code.replace(pattern, replace_value)
                            
                            # 无引号变量名格式
                            no_quotes_pattern = f"{key} = \"REPLACE_ME\""
                            no_quotes_replace = f"{key} = {value}"
                            code = code.replace(no_quotes_pattern, no_quotes_replace)
            
            # 创建服务
            mcp = FastMCP(transport=SseServerTransport())
            
            # 添加服务路由到主应用
            sse_path = f"{self._get_sse_path(service_uuid)}/sse"
            message_path = f"{self._get_sse_path(service_uuid)}/messages"
            
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
                    em_logger.info(f"已删除现有路由: {route.path}")
                except Exception as e:
                    em_logger.error(f"删除路由失败: {route.path}, 错误: {str(e)}")
            
            # 从字符串代码创建模块
            # 使用临时文件创建模块
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
                tmp.write(code.encode('utf-8'))
                tmp_path = tmp.name
            
            # 添加临时文件目录到sys.path以便导入
            dir_name = os.path.dirname(tmp_path)
            file_name = os.path.basename(tmp_path)[:-3]  # 去掉.py后缀
            
            if dir_name not in sys.path:
                sys.path.insert(0, dir_name)
            
            try:
                # 导入模块
                mod = importlib.import_module(file_name)
                importlib.reload(mod)  # 确保每次都重新加载
                
                # 在模块中设置mcp变量
                mod.mcp = mcp
                
                # 重新加载以确保更新
                importlib.reload(mod)
                
                # 注册服务路由
                async def handle_sse(request: Request) -> None:
                    from fastapi.responses import StreamingResponse
                    stream = await mcp.transport.stream(request)
                    return StreamingResponse(stream)
                
                async def handle_messages(request: Request) -> None:
                    body = await request.json()
                    await mcp.transport.handle(body["message"], body.get("attachment"))
                    return {"status": "ok"}
                
                sse_route = Route(sse_path, handle_sse, methods=["GET"])
                message_route = Route(message_path, handle_messages, methods=["POST"])
                
                self._main_app.routes.append(sse_route)
                self._main_app.routes.append(message_route)
                
                # 存储运行服务信息
                self._running_services[service_uuid] = {
                    "mcp": mcp,
                    "module": mod,
                    "service": service
                }
                
                # 更新服务状态
                with get_db() as db:
                    service_record = db.query(McpService).filter(
                        McpService.service_uuid == service_uuid
                    ).first()
                    if service_record:
                        service_record.status = "running"
                        service_record.enabled = True
                        db.commit()
                
                return True
            except Exception as e:
                em_logger.error(f"创建MCP模块失败: {str(e)}")
                # 更新服务状态为错误
                with get_db() as db:
                    service_record = db.query(McpService).filter(
                        McpService.service_uuid == service_uuid
                    ).first()
                    if service_record:
                        service_record.status = "error"
                        db.commit()
                raise e
            finally:
                # 清理临时文件
                try:
                    if tmp_path in sys.path:
                        sys.path.remove(tmp_path)
                    os.unlink(tmp_path)
                except Exception as e:
                    em_logger.error(f"清理临时文件失败: {str(e)}")
        
        except Exception as e:
            em_logger.error(f"创建MCP服务失败: {str(e)}")
            raise e

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
        ]

        for route in list(self._main_app.routes):
            if hasattr(route, 'path') and route.path in routes_to_remove:
                em_logger.info(f"移除路由: {route.path}")
                self._main_app.routes.remove(route)


# 创建全局实例
service_manager = McpServiceManager()
