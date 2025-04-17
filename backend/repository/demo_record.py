import os
from datetime import datetime

from .mcp_base import mcp
from app.services.execution.decorators import record_execution


@record_execution
@mcp.tool()
def get_current_time() -> str:
    """获取当前系统时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@record_execution
@mcp.tool()
def list_files_in_directory(directory_path: str) -> list:
    """列出指定目录中的所有文件
    
    Args:
        directory_path: 要列出文件的目录路径
        
    Returns:
        目录中的文件列表
    """
    try:
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"指定路径不是目录: {directory_path}")
            
        return os.listdir(directory_path)
    except Exception as e:
        # 异常会被装饰器捕获并记录
        raise RuntimeError(f"无法列出目录内容: {str(e)}")


@record_execution
@mcp.tool()
def calculate_sum(numbers: list) -> float:
    """计算数字列表的总和
    
    Args:
        numbers: 要计算总和的数字列表
        
    Returns:
        列表中所有数字的总和
    """
    if not numbers:
        return 0
        
    if not all(isinstance(n, (int, float)) for n in numbers):
        raise ValueError("列表中包含非数字元素")
        
    return sum(numbers) 