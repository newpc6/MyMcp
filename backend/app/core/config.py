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
        self.CORS_CREDENTIALS: bool = config.get(
            "cors", {}).get("credentials", True)
        self.CORS_METHODS: list = config.get("cors", {}).get("methods", ["*"])
        self.CORS_HEADERS: list = config.get("cors", {}).get("headers", ["*"])

        # API设置
        self.API_PREFIX: str = config.get("api", {}).get("prefix", "/api")
        self.API_TITLE: str = config.get("api", {}).get(
            "title", "MCP Server")
        self.API_VERSION: str = config.get("api", {}).get("version", "1.0.0")

        # 服务器设置
        self.HOST: str = config.get("server", {}).get("host", "0.0.0.0")
        self.PORT: int = config.get("server", {}).get("port", 8002)
        self.DEBUG: bool = config.get("server", {}).get("debug", True)

        # Flask设置
        self.FLASK_PORT: int = config.get("flask", {}).get("port", 8003)
        self.ENVIRONMENT: str = config.get(
            "flask", {}).get("environment", "development")

        # 数据库设置
        self.DATABASE_TYPE: str = config.get("database", {}).get(
            "type", "sqlite")  # 数据库类型: sqlite 或 mysql
        self.DATABASE_FILE: str = config.get(
            "database", {}).get("file", "mcp.db")
        # MySQL数据库配置
        self.MYSQL_HOST: str = config.get(
            "database", {}).get("mysql_host", "localhost")
        self.MYSQL_PORT: int = config.get(
            "database", {}).get("mysql_port", 3306)
        self.MYSQL_USER: str = config.get(
            "database", {}).get("mysql_user", "root")
        self.MYSQL_PASSWORD: str = config.get(
            "database", {}).get("mysql_password", "")
        self.MYSQL_DATABASE: str = config.get(
            "database", {}).get("mysql_database", "mcp")

        # 日志设置
        self.LOG_LEVEL: str = config.get("logging", {}).get("level", "info")
        self.LOG_BACKUP_COUNT: int = config.get(
            "logging", {}).get("backup_count", 7)

        # JWT设置
        self.JWT_SECRET_KEY: str = config.get("jwt", {}).get(
            "secret_key", secrets.token_hex(32)
        )
        
        # 统计设置
        self.STATISTICS_INTERVAL: int = config.get("schedule", {}).get(
            "statistics_interval", 10
        )

        # 平台设置
        self.PLATFORM_EGOVA_KB: str = config.get("platform", {}).get(
            "egova-kb", "http://127.0.0.1:8080"
        )

    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        if self.DATABASE_TYPE == "sqlite":
            database_path = os.path.join(self.MCP_BASE_DIR, self.DATABASE_FILE)
            return f"sqlite:///{database_path}"
        elif self.DATABASE_TYPE == "mysql":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        else:
            raise ValueError(f"不支持的数据库类型: {self.DATABASE_TYPE}")


settings = Settings()
