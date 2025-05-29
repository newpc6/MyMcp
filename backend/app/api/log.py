"""
示例API模块

展示如何在API中使用日志功能
"""

from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request
from pydantic import BaseModel, ValidationError

from app.utils.logging import mcp_logger


class LogTestRequest(BaseModel):
    """日志测试请求模型"""
    message: str
    level: str = "info"


async def log_test(request: Request):
    """
    测试日志功能
    
    Args:
        request: 请求对象，包含查询参数
        
    Returns:
        JSONResponse: 操作结果
    """
    # 获取请求参数
    params = request.query_params
    message = params.get("message", "测试日志消息")
    
    # 记录不同级别的日志
    mcp_logger.debug(f"调试日志: {message}")
    mcp_logger.info(f"信息日志: {message}")
    mcp_logger.warning(f"模块警告日志: {message}")
    
    return JSONResponse({
        "message": "日志已记录",
        "status": "success"
    })


async def log_level(request: Request):
    """
    测试不同级别的日志
    
    Args:
        request: 请求对象
        
    Returns:
        JSONResponse: 操作结果
    """
    try:
        # 获取JSON请求体
        data = await request.json()
        request_data = LogTestRequest(**data)
        
        level = request_data.level.lower()
        message = request_data.message
        
        if level == "debug":
            mcp_logger.debug(message)
        elif level == "info":
            mcp_logger.info(message)
        elif level == "warning":
            mcp_logger.warning(message)
        elif level == "error":
            mcp_logger.error(message)
        elif level == "critical":
            mcp_logger.critical(message)
        else:
            return JSONResponse({"detail": "无效的日志级别"}, status_code=400)
        
        return JSONResponse({
            "message": f"已记录{level}级别日志",
            "status": "success"
        })
    except ValidationError as e:
        return JSONResponse({"detail": str(e)}, status_code=422)
    except Exception as e:
        mcp_logger.error(f"记录日志时出错: {str(e)}")
        return JSONResponse({"detail": "记录日志时出错"}, status_code=500)


def get_router():
    """获取日志路由"""
    routes = [
        Route("/log_test", endpoint=log_test, methods=["GET"]),
        Route("/log_level", endpoint=log_level, methods=["POST"])
    ]
    
    return routes 