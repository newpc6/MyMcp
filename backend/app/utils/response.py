"""
统一的API响应格式工具

使用Starlette框架
"""
from starlette.responses import JSONResponse


def success_response(
    data=None, 
    message="操作成功", 
    code=0, 
    http_status_code=200
):
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 业务代码，默认0表示成功
        http_status_code: HTTP状态码
    
    Returns:
        JSON响应
    """
    response = {
        "code": code,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return JSONResponse(content=response, status_code=http_status_code)


def error_response(
    message="操作失败", 
    data=None, 
    code=400, 
    http_status_code=400
):
    """
    错误响应
    
    Args:
        message: 错误消息
        data: 额外的错误数据
        code: 业务代码，默认400表示请求错误
        http_status_code: HTTP状态码
    
    Returns:
        JSON响应
    """
    response = {
        "code": code,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return JSONResponse(content=response, status_code=http_status_code) 