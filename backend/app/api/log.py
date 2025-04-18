"""
示例API模块

展示如何在API中使用日志功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.logging import em_logger

router = APIRouter()


class LogTestRequest(BaseModel):
    """日志测试请求模型"""
    message: str
    level: str = "info"


@router.get("/log_test")
async def log_test(message: str = "测试日志消息"):
    """
    测试日志功能
    
    Args:
        message: 要记录的日志消息
        
    Returns:
        dict: 操作结果
    """
    # 记录不同级别的日志
    em_logger.debug(f"调试日志: {message}")
    em_logger.info(f"信息日志: {message}")
    em_logger.warning(f"模块警告日志: {message}")
    
    return {
        "message": "日志已记录",
        "status": "success"
    }


@router.post("/log_level")
async def log_level(request: LogTestRequest):
    """
    测试不同级别的日志
    
    Args:
        request: 日志请求
        
    Returns:
        dict: 操作结果
    """
    level = request.level.lower()
    message = request.message
    
    try:
        if level == "debug":
            em_logger.debug(message)
        elif level == "info":
            em_logger.info(message)
        elif level == "warning":
            em_logger.warning(message)
        elif level == "error":
            em_logger.error(message)
        elif level == "critical":
            em_logger.critical(message)
        else:
            raise HTTPException(status_code=400, detail="无效的日志级别")
        
        return {
            "message": f"已记录{level}级别日志",
            "status": "success"
        }
    except Exception as e:
        em_logger.error(f"记录日志时出错: {str(e)}")
        raise HTTPException(status_code=500, detail="记录日志时出错") 