from fastapi import APIRouter

# from .tools import router as tools_router
# from .resources import router as resources_router
# from .modules import router as modules_router
# from .execution import router as execution_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from . import tools, resources, modules, protocols, mcp_service, history, execution
# router = APIRouter()

# router.include_router(
#     tools_router,
#     prefix="/tools",
#     tags=["tools"]
# )
# router.include_router(
#     resources_router,
#     prefix="/resources",
#     tags=["resources"]
# )
# router.include_router(
#     modules_router,
#     prefix="/modules",
#     tags=["modules"]
# )
# router.include_router(
#     execution_router,
#     prefix="/execute",
#     tags=["execution"]
# )


def get_router(app):
    @app.get("/")
    async def root():
        return {
            "message": "欢迎使用 Egova AI MCP Server API",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }

    # 注册API路由
    app.include_router(
        tools.router,
        prefix=f"{settings.API_PREFIX}/tools",
        tags=["tools"]
    )
    app.include_router(
        resources.router,
        prefix=f"{settings.API_PREFIX}/resources",
        tags=["resources"]
    )
    app.include_router(
        modules.router,
        prefix=f"{settings.API_PREFIX}/modules",
        tags=["modules"]
    )
    app.include_router(
        protocols.router,
        prefix=f"{settings.API_PREFIX}/protocols",
        tags=["protocols"]
    )
    app.include_router(
        mcp_service.router,
        prefix=f"{settings.API_PREFIX}/mcp/service",
        tags=["mcp_service"]
    )
    app.include_router(
        history.router,
        prefix=f"{settings.API_PREFIX}/history",
        tags=["history"]
    )
    app.include_router(
        execution.router,
        prefix=f"{settings.API_PREFIX}/execute",
        tags=["execute"]
    )
    return app
