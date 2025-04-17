import time
import inspect
from typing import Any, Dict, Callable

from ..history.service import history_service


def record_tool_call(
    func_name: str, 
    description: str, 
    parameters: Dict[str, Any],
    result: Any
):
    """
    手动记录工具调用，适用于函数内部调用
    
    Args:
        func_name: 函数名称
        description: 函数描述/文档
        parameters: 函数参数
        result: 函数返回结果
    """
    status = ("success" if not isinstance(result, dict) 
              or "error" not in result else "failed")
    execution_time = 0  # 无法计算执行时间
    
    try:
        history_service.record_tool_execution(
            tool_name=func_name,
            description=description,
            parameters=parameters,
            result=result,
            status=status,
            execution_time=execution_time
        )
    except Exception as e:
        print(f"记录工具执行历史失败: {e}")


def execute_with_record(func: Callable, *args, **kwargs) -> Any:
    """
    执行函数并记录其执行，可在函数内部调用
    
    用法示例:
    ```
    from app.services.execution.utils import execute_with_record
    
    @mcp.tool()
    def my_tool(param1, param2):
        # 处理逻辑
        result = execute_with_record(actual_function, param1, param2)
        return result
    ```
    """
    # 获取函数文档
    description = inspect.getdoc(func) or ""
    
    # 将参数打包成字典
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    parameters = dict(bound_args.arguments)
    
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