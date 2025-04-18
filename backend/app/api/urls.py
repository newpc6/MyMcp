from app.core.config import settings
from . import (
    tools, resources, modules, protocols, mcp_service, 
    history, execution, log
)


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
    app.include_router(
        log.router,
        prefix=f"{settings.API_PREFIX}/log",
        tags=["log"]
    )
    return app
