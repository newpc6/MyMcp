"""
静态文件服务模块

提供静态文件的访问功能，包括前端资源
"""
import os
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from app.core.config import settings
from app.utils.logging import mcp_logger

# 获取前端dist目录的绝对路径
DIST_DIR = os.path.join(settings.MCP_BASE_DIR, "dist")

# 如果backend/dist目录存在，使用backend/dist
BACKEND_DIST_DIR = os.path.join(settings.MCP_BASE_DIR, "backend", "dist")
if os.path.exists(BACKEND_DIST_DIR):
    DIST_DIR = BACKEND_DIST_DIR
    mcp_logger.info(f"使用前端资源目录: {DIST_DIR}")

# 检查dist目录是否存在
if not os.path.exists(DIST_DIR):
    mcp_logger.error(f"前端资源目录不存在: {DIST_DIR}")
    # raise FileNotFoundError(f"前端资源目录不存在: {DIST_DIR}")

# 检查assets目录是否存在
ASSETS_DIR = os.path.join(DIST_DIR, "assets")
if not os.path.exists(ASSETS_DIR):
    mcp_logger.warning(f"前端资源目录中没有assets子目录: {ASSETS_DIR}")


try:
    # 创建StaticFiles实例
    static_files = StaticFiles(directory=DIST_DIR)
except Exception:
    mcp_logger.error(f"未找到dist前端资源目录: {DIST_DIR}")


try:
    # 创建专门用于assets的StaticFiles实例
    assets_files = (StaticFiles(directory=ASSETS_DIR) 
                    if os.path.exists(ASSETS_DIR) else None)
except Exception:
    mcp_logger.error(f"未找到assets目录: {ASSETS_DIR}")


async def index(request):
    """提供前端首页"""
    mcp_logger.debug(f"提供前端首页: {request.url.path}")
    return FileResponse(os.path.join(DIST_DIR, "index.html"))


def get_media_type(file_path):
    """根据文件扩展名获取适当的媒体类型"""
    if file_path.endswith('.js'):
        return 'application/javascript'
    elif file_path.endswith('.mjs'):
        return 'application/javascript'
    elif file_path.endswith('.css'):
        return 'text/css'
    elif file_path.endswith('.html'):
        return 'text/html'
    elif file_path.endswith('.json'):
        return 'application/json'
    elif file_path.endswith('.png'):
        return 'image/png'
    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        return 'image/jpeg'
    elif file_path.endswith('.gif'):
        return 'image/gif'
    elif file_path.endswith('.svg'):
        return 'image/svg+xml'
    elif file_path.endswith('.woff'):
        return 'font/woff'
    elif file_path.endswith('.woff2'):
        return 'font/woff2'
    elif file_path.endswith('.ttf'):
        return 'font/ttf'
    elif file_path.endswith('.eot'):
        return 'application/vnd.ms-fontobject'
    elif file_path.endswith('.ico'):
        return 'image/x-icon'
    return None


async def spa_routing(request):
    """
    处理SPA路由，返回index.html
    
    这个函数用于处理前端路由，使得刷新页面时不会返回404
    """
    path = request.path_params.get("path", "")
    full_path = request.url.path
    mcp_logger.debug(f"SPA路由处理: {path}, 完整路径: {full_path}")
    
    # MCP服务路径应该在路由注册时被正确处理，不应该到达这里
    if full_path.startswith("/mcp-"):
        mcp_logger.warning(f"MCP路径到达SPA路由: {full_path}")
        # 返回404，因为MCP路由应该已经处理了这个请求
        from starlette.responses import PlainTextResponse
        return PlainTextResponse(
            "MCP服务路径未找到。此请求应该由MCP路由处理。",
            status_code=404
        )
    
    # API请求不应该由SPA路由处理器捕获
    if full_path.startswith("/api") or path.startswith("api"):
        mcp_logger.warning(f"API路径未被API路由捕获: {full_path}")
        from starlette.responses import PlainTextResponse
        return PlainTextResponse(
            "API路径未找到。此请求不应由SPA路由处理。",
            status_code=404
        )
    
    # 检查是否为静态资源路径
    if path.startswith("assets/"):
        asset_path = path[7:]  # 移除 "assets/" 前缀
        file_path = os.path.join(ASSETS_DIR, asset_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            mcp_logger.debug(f"直接提供静态资源: {file_path}")
            media_type = get_media_type(file_path)            
            return FileResponse(file_path, media_type=media_type)
    
    # 否则返回index.html
    return FileResponse(os.path.join(DIST_DIR, "index.html"))


async def asset_file(request):
    """提供assets目录下的静态文件"""
    path = request.path_params.get("path", "")
    mcp_logger.debug(f"提供assets文件: {path}")
    file_path = os.path.join(ASSETS_DIR, path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        media_type = get_media_type(file_path)
        return FileResponse(file_path, media_type=media_type)
    
    # 如果文件不存在，返回404
    return FileResponse(
        status_code=404,
        content="File not found"
    )


def get_static_mount():
    """获取静态文件挂载点"""
    if static_files is None:
        mcp_logger.error("静态文件挂载点不存在")
        return None
    return static_files


def get_assets_mount():
    """获取assets目录的挂载点"""
    if assets_files is None:
        mcp_logger.error("assets目录挂载点不存在")
        return None
    return assets_files


def get_router():
    """获取静态文件路由配置"""
    return [
        {
            "path": "/",
            "endpoint": index,
            "methods": ["GET"],
            "name": "index"
        },
        {
            "path": "/assets/{path:path}",
            "endpoint": asset_file,
            "methods": ["GET"],
            "name": "asset_file"
        },
        {
            "path": "/{path:path}",
            "endpoint": spa_routing,
            "methods": ["GET"],
            "name": "spa_routing",
            "include_in_schema": False  # 不在API文档中显示
        }
    ]
