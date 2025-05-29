"""
日志记录器模块

提供日志记录功能，支持控制台输出和文件输出
"""

import logging
import os
import time
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


def get_current_timestamp() -> float:
    """
    获取当前时间戳
    
    Returns:
        float: 当前时间戳
    """
    return time.time()


def log_api_call(
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    error: Optional[Exception] = None,
    logger: Optional[logging.Logger] = None,
    start_time: Optional[float] = None
) -> None:
    """
    记录 API 调用日志

    Args:
        request: 请求对象
        response: 响应对象
        error: 异常对象
        logger: 日志记录器，如果为None则使用默认的mcp_logger
        start_time: 请求开始时间戳，用于计算处理耗时
    """
    if logger is None:
        logger = mcp_logger

    message = ''
    if request:
        message = f"请求: {request.method} {request.url.path}"
        if request.query_params:
            message += f" 查询参数: {request.query_params}"

    if response:
        message += f" 响应状态码: {response.status_code}"

    # 计算处理耗时
    if start_time is not None:
        duration = time.time() - start_time
        duration_ms = duration * 1000
        message += f" 处理耗时: {duration_ms:.1f}毫秒"

    if error:
        message += f" 错误: {str(error)}"

    logger.info(message)


# 创建默认的日志记录器
mcp_logger = get_logger('mcp')
