"""
MCP服务管理器模块

这是动态发布MCP服务的核心功能实现，它管理多个独立的MCP服务实例，
每个实例都有自己的路由路径。用户可以为不同的模块发布单独的MCP服务，
并且可以实时启动和停止这些服务。
"""
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


class McpServiceManager:
    """MCP服务管理器，负责启动和停止MCP服务"""
    
    _instance = None
    _main_app = None
    _server = None
    _running_services: Dict[str, Dict] = {}  # 存储正在运行的服务
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(McpServiceManager, cls).__new__(cls)
        return cls._instance
    
    def init_app(self, app, server):
        """初始化应用程序实例，保存引用"""
        self._main_app = app
        self._server = server
        self._initialize()
    
    def _initialize(self):
        """初始化管理器"""
        self._load_services_from_db()
    
    def _load_services_from_db(self):
        """从数据库中加载已存在的服务"""
        if not self._main_app:
            em_logger.warning("主应用程序未初始化，无法加载服务")
            return
            
        with get_db() as db:
            services = db.query(McpService).filter(
                McpService.status == "running"
            ).all()
            for service in services:
                # 尝试重新启动已发布的服务
                try:
                    module = db.query(McpModule).filter(
                        McpModule.id == service.module_id
                    ).first()
                    if module:
                        self._create_service_routes(service, module)
                        em_logger.info(f"已重新启动服务: {service.service_uuid}")
                except Exception as e:
                    msg = f"重新启动服务失败 {service.service_uuid}: {str(e)}"
                    em_logger.error(msg)
                    service.status = "error"
                    db.commit()
    
    def _get_sse_path(self, service_uuid: str) -> str:
        """获取SSE URL"""
        return f"/mcp-{service_uuid}"
    
    def publish_service(self, module_id: int) -> McpService:
        """发布一个MCP模块服务
        
        Args:
            module_id: MCP模块ID
            
        Returns:
            McpService: 创建的服务记录
        """
        if not self._main_app:
            raise ValueError("主应用程序未初始化，无法发布服务")
            
        # 检查是否已经发布
        with get_db() as db:
            existing = db.query(McpService).filter(
                McpService.module_id == module_id
            ).first()
            
            if existing and existing.status == "running":
                raise ValueError(f"模块 {module_id} 已经发布服务")
                
            # 检查模块是否存在
            module = db.query(McpModule).filter(
                McpModule.id == module_id
            ).first()
            if not module:
                raise ValueError(f"模块不存在: {module_id}")
                
            # 生成唯一ID
            service_uuid = str(uuid.uuid4()) if not existing else existing.service_uuid
            
            # 构建SSE URL
            sse_url = f"{settings.SSE_SERVER_URL}{self._get_sse_path(service_uuid)}/sse"
            
            if existing:
                # 更新现有服务
                existing.sse_url = sse_url
                existing.status = "running"
                service_record = existing
            else:
                # 创建新的服务记录
                service_record = McpService(
                    module_id=module_id,
                    service_uuid=service_uuid,
                    sse_url=sse_url,
                    status="running"
                )
                db.add(service_record)
                
            db.commit()
            db.refresh(service_record)
        
        # 创建服务路由
        self._create_service_routes(service_record, module)
        
        return service_record
    
    def stop_service(self, service_uuid: str) -> bool:
        """停止MCP服务
        
        Args:
            service_uuid: 服务UUID
            
        Returns:
            bool: 是否成功停止
        """
        # 检查服务是否存在
        if service_uuid not in self._running_services:
            with get_db() as db:
                service = db.query(McpService).filter(
                    McpService.service_uuid == service_uuid
                ).first()
                if not service:
                    return False
                service.status = "stopped"
                db.commit()
            return True
            
        # 获取服务信息并停止服务
        service_info = self._running_services.pop(service_uuid, None)
        if service_info:
            # 移除路由
            if self._main_app:
                self._remove_service_routes(service_uuid)
        
        # 更新数据库状态
        with get_db() as db:
            service = db.query(McpService).filter(
                McpService.service_uuid == service_uuid
            ).first()
            if service:
                service.status = "stopped"
                db.commit()
        
        return True
    
    def delete_service(self, service_uuid: str) -> bool:
        """完全删除MCP服务
        
        Args:
            service_uuid: 服务UUID
            
        Returns:
            bool: 是否成功删除
        """
        # 先停止服务
        self.stop_service(service_uuid)
        
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
            
            # 获取模块名称
            module = db.query(McpModule).filter(
                McpModule.id == service.module_id
            ).first()
            module_name = module.name if module else None
            
            # 转换为字典
            return {
                "id": service.id,
                "module_id": service.module_id,
                "module_name": module_name,
                "service_uuid": service.service_uuid,
                "status": service.status,
                "sse_url": service.sse_url,
                "created_at": service.created_at.isoformat() 
                    if service.created_at else None,
                "updated_at": service.updated_at.isoformat() 
                    if service.updated_at else None
            }
    
    def list_services(self, module_id: Optional[int] = None) -> List[Dict]:
        """列出所有服务
        
        Args:
            module_id: 可选的模块ID筛选
            
        Returns:
            List[Dict]: 服务列表
        """
        with get_db() as db:
            query = db.query(McpService)
            if module_id is not None:
                query = query.filter(McpService.module_id == module_id)
                
            services = query.all()
            
            # 获取所有使用的模块ID
            module_ids = [service.module_id for service in services]
            
            # 批量查询模块信息
            modules_map = {}
            if module_ids:
                modules = db.query(McpModule).filter(
                    McpModule.id.in_(module_ids)
                ).all()
                modules_map = {m.id: m.name for m in modules}
            
            return [
                {
                    "id": service.id,
                    "module_id": service.module_id,
                    "module_name": modules_map.get(service.module_id),
                    "service_uuid": service.service_uuid,
                    "status": service.status,
                    "sse_url": service.sse_url,
                    "created_at": service.created_at.isoformat() 
                        if service.created_at else None,
                    "updated_at": service.updated_at.isoformat() 
                        if service.updated_at else None
                }
                for service in services
            ]
    
    def _create_service_routes(self, service: McpService, module: McpModule):
        """为服务创建路由"""
        if not self._main_app:
            raise ValueError("主应用程序未初始化，无法创建路由")
        
        # 为每个服务创建独立的FastMCP实例，而不是使用共享实例
        self._server = FastMCP(
            name=f"{module.name} MCP Server",
            host=settings.HOST,
            port=settings.PORT,
        )
        
        # 加载模块代码
        if module.code:
            # 编译并执行模块代码
            namespace = {}
            exec(module.code, namespace)
            
            # 注册模块中的工具函数到这个独立实例
            for name, obj in namespace.items():
                if callable(obj) and name.startswith("tool_"):
                    self._server.add_tool(obj, name=name)
        
        # 创建SSE应用
        service_uuid = service.service_uuid
        sse = SseServerTransport(f"{self._get_sse_path(service_uuid)}/messages/")
        
        # 创建SSE处理函数，使用特定服务的server实例
        async def handle_sse(request: Request) -> None:
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
            ) as streams:
                await self._server._mcp_server.run(
                    streams[0],
                    streams[1],
                    self._server._mcp_server.create_initialization_options(),
                )
        
        # 添加服务路由到主应用
        route_path = f"{self._get_sse_path(service_uuid)}/sse"
        mount_path = f"{self._get_sse_path(service_uuid)}/messages"
        
        self._main_app.add_route(route_path, handle_sse)
        self._main_app.mount(mount_path, sse.handle_post_message)
        
        # 保存服务信息
        self._running_services[service_uuid] = {
            "server": self._server,  # 存储服务特定的FastMCP实例
            "routes": [route_path, mount_path]
        }
    
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