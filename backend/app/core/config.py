import os
import json
import secrets
from typing import Dict, Any, List
from pathlib import Path


class Settings:
    def __init__(self):
        # 获取配置文件路径
        config_path = Path(__file__).parent.parent.parent / "config.json"
        
        # 读取配置文件
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}
        
        # 基础路径设置
        self.MCP_BASE_DIR: str = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.MCP_MODULES: Dict[str, Any] = {}
        
        # CORS设置
        self.CORS_ORIGINS: list = config.get("cors", {}).get("origins", ["*"])
        self.CORS_CREDENTIALS: bool = config.get("cors", {}).get("credentials", True)
        self.CORS_METHODS: list = config.get("cors", {}).get("methods", ["*"])
        self.CORS_HEADERS: list = config.get("cors", {}).get("headers", ["*"])
        
        # API设置
        self.API_PREFIX: str = config.get("api", {}).get("prefix", "/api")
        self.API_TITLE: str = config.get("api", {}).get("title", "Egova AI MCP Server")
        self.API_VERSION: str = config.get("api", {}).get("version", "1.0.0")
        
        # 服务器设置
        self.HOST: str = config.get("server", {}).get("host", "0.0.0.0")
        self.PORT: int = config.get("server", {}).get("port", 8002)
        self.DEBUG: bool = config.get("server", {}).get("debug", True)
        self.SSE_SERVER_URL: str = config.get("server", {}).get("sse_server_url", "http://10.4.1.132:8002")
        
        # Flask设置
        self.FLASK_PORT: int = config.get("flask", {}).get("port", 8003)
        self.ENVIRONMENT: str = config.get("flask", {}).get("environment", "development")
        
        # MCP设置
        self.MCP_PORT: int = config.get("mcp", {}).get("port", 8002)
        self.MCP_SSE_URL: str = config.get("mcp", {}).get("sse_url", f"http://localhost:{self.MCP_PORT}/sse")
        self.MCP_ENABLED_TOOLS: List[str] = config.get("mcp", {}).get("enabled_tools", [])
        
        # 数据库设置
        self.DATABASE_FILE: str = config.get("database", {}).get("file", "egova-mcp.db")
        
        # 日志设置
        self.LOG_LEVEL: str = config.get("logging", {}).get("level", "info")
        self.LOG_BACKUP_COUNT: int = config.get("logging", {}).get("backup_count", 7)
        
        # JWT设置
        self.JWT_SECRET_KEY: str = config.get("jwt", {}).get(
            "secret_key", secrets.token_hex(32)
        )


settings = Settings() 