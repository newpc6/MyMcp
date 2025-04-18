"""
日志记录器模块

提供日志记录功能，支持控制台输出和文件输出
"""

import logging
import os
from datetime import datetime
from typing import Optional
from fastapi import Request, Response

# 创建日志目录
log_dir = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )
    ),
    'log'
)
os.makedirs(log_dir, exist_ok=True)

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        
    Returns:
        logging.Logger: 日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果已经有处理器，则不再添加
    if logger.handlers:
        return logger
        
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)
    
    # 创建文件处理器
    log_file = os.path.join(
        log_dir,
        f'{name}_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(file_handler)
    
    return logger

def log_api_call(
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    error: Optional[Exception] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    记录 API 调用日志
    
    Args:
        request: 请求对象
        response: 响应对象
        error: 异常对象
        logger: 日志记录器，如果为None则使用默认的em_logger
    """
    if logger is None:
        logger = em_logger
        
    if request:
        logger.info(f"请求: {request.method} {request.url.path}")
        if request.query_params:
            logger.info(f"查询参数: {request.query_params}")
            
    if response:
        logger.info(f"响应状态码: {response.status_code}")
        
    if error:
        logger.error(f"错误: {str(error)}")

# 创建默认的日志记录器
em_logger = get_logger('egova-mcp')
# mcp_logger = get_logger('mcp') 