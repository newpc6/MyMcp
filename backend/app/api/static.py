"""
静态文件服务模块

提供静态文件的访问功能，包括前端资源
"""
import os
from pathlib import Path
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from app.core.config import settings
from app.utils.logging import em_logger

# 获取前端dist目录的绝对路径
DIST_DIR = os.path.join(settings.MCP_BASE_DIR, "dist")

# 如果backend/dist目录存在，使用backend/dist
BACKEND_DIST_DIR = os.path.join(settings.MCP_BASE_DIR, "backend", "dist")
if os.path.exists(BACKEND_DIST_DIR):
    DIST_DIR = BACKEND_DIST_DIR
    em_logger.info(f"使用前端资源目录: {DIST_DIR}")

# 检查dist目录是否存在
if not os.path.exists(DIST_DIR):
    em_logger.error(f"前端资源目录不存在: {DIST_DIR}")
    # raise FileNotFoundError(f"前端资源目录不存在: {DIST_DIR}")

# 检查assets目录是否存在
ASSETS_DIR = os.path.join(DIST_DIR, "assets")
if not os.path.exists(ASSETS_DIR):
    em_logger.warning(f"前端资源目录中没有assets子目录: {ASSETS_DIR}")

# 创建StaticFiles实例
static_files = StaticFiles(directory=DIST_DIR)
# 创建专门用于assets的StaticFiles实例
assets_files = StaticFiles(directory=ASSETS_DIR) if os.path.exists(ASSETS_DIR) else None

async def index(request):
    """提供前端首页"""
    em_logger.debug(f"提供前端首页: {request.url.path}")
    return FileResponse(os.path.join(DIST_DIR, "index.html"))

async def spa_routing(request):
    """
    处理SPA路由，返回index.html
    
    这个函数用于处理前端路由，使得刷新页面时不会返回404
    """
    path = request.path_params.get("path", "")
    em_logger.debug(f"SPA路由处理: {path}")
    
    # 如果是/api开头的路径，不进行处理，直接返回404
    # 这样可以避免干扰API调用
    if path.startswith("api/"):
        em_logger.debug(f"API路径不由SPA处理: {path}")
        from starlette.responses import Response
        return Response(status_code=404, content="Not Found")
    
    # 检查是否为静态资源路径
    if path.startswith("assets/"):
        asset_path = path[7:]  # 移除 "assets/" 前缀
        file_path = os.path.join(ASSETS_DIR, asset_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            em_logger.debug(f"直接提供静态资源: {file_path}")
            return FileResponse(file_path)
    
    # 否则返回index.html
    return FileResponse(os.path.join(DIST_DIR, "index.html"))

async def asset_file(request):
    """提供assets目录下的静态文件"""
    path = request.path_params.get("path", "")
    em_logger.debug(f"提供assets文件: {path}")
    file_path = os.path.join(ASSETS_DIR, path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # 如果文件不存在，返回404
    return FileResponse(
        status_code=404,
        content="File not found"
    )

def get_static_mount():
    """获取静态文件挂载点"""
    return static_files

def get_assets_mount():
    """获取assets目录的挂载点"""
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
        }
        # {
        #     "path": "/{path:path}",
        #     "endpoint": spa_routing,
        #     "methods": ["GET"],
        #     "name": "spa_routing"
        # }
    ]
