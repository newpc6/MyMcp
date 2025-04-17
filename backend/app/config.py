import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API相关配置
    API_PREFIX: str = "/api"
    DEBUG: bool = True
    
    # 工具文件根目录
    TOOLS_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"
    )
    
    # 资源文件根目录
    RESOURCES_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources"
    )
    
    # 模块文件根目录
    MODULES_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules"
    )
    
    # 协议文件根目录
    PROTOCOLS_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "protocols"
    )
    
    # MCP服务相关配置
    MCP_SERVICE_CMD: str = "python -m repository.server"
    MCP_SERVICE_PID_FILE: str = "/tmp/mcp_server.pid"
    MCP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"


settings = Settings() 