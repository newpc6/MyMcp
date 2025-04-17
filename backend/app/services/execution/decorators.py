import time
import functools
import inspect
from typing import Callable

from ..history.service import history_service


def record_execution(func: Callable) -> Callable:
    """
    装饰器: 用于记录mcp.tool方法的调用记录
    
    用法示例:
    ```
    from repository.mcp_base import mcp
    from app.services.execution.decorators import record_execution
    
    @record_execution
    @mcp.tool()
    def my_tool(param1: str, param2: int) -> str:
        \"\"\"工具说明\"\"\"
        return "结果"
    ```
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 获取函数签名和参数信息
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        parameters = dict(bound_args.arguments)
        
        # 获取函数文档
        description = inspect.getdoc(func) or ""
        
        # 记录开始时间
        start_time = time.time()
        status = "success"
        result = None
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            status = "failed"
            # 记录异常信息
            result = {"error": str(e)}
            # 重新抛出异常
            raise
        finally:
            # 计算执行时间（毫秒）
            execution_time = int((time.time() - start_time) * 1000)
            
            # 记录执行历史
            try:
                history_service.record_tool_execution(
                    tool_name=func.__name__,
                    description=description,
                    parameters=parameters,
                    result=result,
                    status=status,
                    execution_time=execution_time
                )
            except Exception as e:
                print(f"记录工具执行历史失败: {e}")
    
    return wrapper 