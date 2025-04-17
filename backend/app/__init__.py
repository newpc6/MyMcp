# """
# Egova AI MCP Server 应用程序入口
# """

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from .core.config import settings
# # from .api import tools, resources, modules  # 注释掉原来的导入
# from .api.urls import get_router  # 导入 urls.py 中的聚合路由

# app = FastAPI(
#     title=settings.API_TITLE,
#     version=settings.API_VERSION,
#     debug=settings.DEBUG
# )

# def create_app() -> FastAPI:
#     # app = FastAPI(title="Egova AI MCP Server", debug=settings.DEBUG)
    
#     get_router(app)

#     # # 注释掉原先单独注册的路由
#     # app.include_router(
#     #     tools.router,
#     #     prefix=settings.API_PREFIX
#     # )
#     # app.include_router(
#     #     resources.router,
#     #     prefix=settings.API_PREFIX
#     # )
#     # app.include_router(
#     #     modules.router,
#     #     prefix=settings.API_PREFIX
#     # )
    
#     return app


# def init_app():
#     """
#     初始化应用程序
    
#     Returns:
#         fastapi.FastAPI: FastAPI应用程序实例
#     """
#     from app.models.engine import init_db
#     app = create_app()
#     # 初始化数据库
#     init_db()
    
#     # 返回应用程序实例
#     return app 