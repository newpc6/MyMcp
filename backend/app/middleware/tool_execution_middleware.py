"""
MCP工具执行中间件

用于拦截MCP工具调用并记录执行信息
"""

import json
import time
import re
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import Response
from starlette.datastructures import MutableHeaders

from ..utils.logging import mcp_logger
from ..services.history.service import HistoryService
from ..models.engine import get_db
from ..models.modules.mcp_services import McpService


class ToolExecutionMiddleware(BaseHTTPMiddleware):
    """MCP工具执行中间件，拦截MCP工具调用并记录执行信息"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.history_service = HistoryService()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        处理请求并记录MCP工具执行信息
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
            
        Returns:
            响应对象
        """
        # 检查是否是MCP工具调用路径
        path = request.url.path
        # 克隆请求体以便多次读取
        body_bytes = await request.body()
        if not self._is_tool_execution_path(path, body_bytes):
            return await call_next(request)
        
        start_time = time.time()
        tool_name = None
        parameters = {}
        result = None
        status = "success"
        service_id = None
        module_id = None
        
        # 提取 service_id
        service_id_match = re.search(r'/mcp-([^/]+)', path)
        if service_id_match:
            service_id = service_id_match.group(1)
            
            # 根据 service_id 查找关联的模块 ID
            try:
                with get_db() as db:
                    service = db.query(McpService).filter(
                        McpService.service_uuid == service_id
                    ).first()
                    if service:
                        module_id = service.module_id
            except Exception as e:
                mcp_logger.warning(f"查询服务关联模块时出错: {str(e)}")        
            try:
                # 尝试获取请求参数
                if request.method in ["POST", "PUT"]:
                    try:
                        body = json.loads(body_bytes)
                        mcp_logger.info(f"{path} 请求体: {body}")
                        
                        method = body.get("method")
                        if method == "tools/call":
                            params = body.get("params", {})
                            tool_name = params.get("name")
                            parameters = params.get("arguments", {})
                    except Exception as e:
                        mcp_logger.warning(f"解析请求体时出错: {str(e)}")            
                # 处理请求
                return await call_next(request)       
            except Exception as e:
                mcp_logger.error(f"处理MCP工具执行时出错: {str(e)}")
                status = "error"
                # 继续处理请求，不中断
                return await call_next(request)        
            finally:
                # 计算执行时间
                execution_time = int((time.time() - start_time) * 1000)  # 转换为毫秒
                
                # 记录工具执行
                if tool_name:
                    try:
                        self.history_service.record_tool_execution(
                            tool_name=tool_name,
                            service_id=service_id,
                            module_id=module_id,
                            description=f"执行工具 {tool_name}",
                            parameters=parameters,
                            result=None,
                            status=status,
                            execution_time=execution_time
                        )
                        mcp_logger.info(
                            f"记录工具执行: {tool_name}, 服务: {service_id}, "
                            f"模块: {module_id}, 状态: {status}, "
                            f"执行时间: {execution_time}ms"
                        )
                    except Exception as e:
                        mcp_logger.error(f"记录工具执行时出错: {str(e)}")
    
    def _is_tool_execution_path(self, path: str, body_bytes: bytes) -> bool:
        """检查路径是否为MCP工具执行路径"""
        if "/messages" in path and "mcp-" in path:
            # 尝试获取请求参数
            try:
                body = json.loads(body_bytes)                    
                method = body.get("method")
                if method == "tools/call":
                    return True
            except Exception as e:
                mcp_logger.warning(f"解析请求体时出错: {str(e)}")
                return False
        return False
