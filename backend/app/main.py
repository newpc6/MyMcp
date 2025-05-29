"""
Egova AI MCP Server 应用程序入口
"""

import signal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.urls import get_router  # 导入 urls.py 中的聚合路由
from .middleware.logging_middleware import APILoggingMiddleware
from .utils.logging import mcp_logger

def create_app() -> FastAPI:
    return None
