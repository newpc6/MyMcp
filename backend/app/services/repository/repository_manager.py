"""
仓库管理工具，用于扫描和管理repository目录中的模块
"""
import os
import sys
import inspect
import importlib
from typing import List, Dict, Any, Callable

# 获取项目根目录
project_root = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
)

# 获取repository目录路径
repository_dir = os.path.join(project_root, "repository")

# 添加项目根目录到Python路径
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def get_repository_tools() -> List[Dict[str, Any]]:
    """
    扫描repository目录中的所有工具

    Returns:
        List[Dict[str, Any]]: 工具信息列表
    """
    tools_list = []

    # 获取repository目录中的所有.py文件
    py_files = []
    for root, _, files in os.walk(repository_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('_'):
                rel_path = os.path.relpath(
                    os.path.join(root, file), project_root
                )
                module_path = rel_path.replace(
                    os.path.sep, '.'
                ).replace('.py', '')
                py_files.append(module_path)

    # 导入每个模块并查找工具函数
    for module_path in py_files:
        try:
            module = importlib.import_module(module_path)
            
            # 检查模块中的所有函数
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and not name.startswith('_'):
                    # 提取函数信息
                    description = obj.__doc__ or f"{name} 函数"
                    
                    # 创建工具信息
                    tool_info = {
                        "module_path": module_path,
                        "function_name": name,
                        "description": description.strip(),
                        "parameters": _get_function_parameters(obj)
                    }
                    
                    tools_list.append(tool_info)
        except Exception as e:
            print(f"导入模块 {module_path} 时出错: {str(e)}")
    
    return tools_list


def _get_function_parameters(func: Callable) -> List[Dict[str, Any]]:
    """
    获取函数的参数信息

    Args:
        func (Callable): 要分析的函数

    Returns:
        List[Dict[str, Any]]: 参数信息列表
    """
    signature = inspect.signature(func)
    params = []
    
    for name, param in signature.parameters.items():
        # 跳过self参数
        if name == 'self':
            continue
        
        param_type = (
            str(param.annotation) 
            if param.annotation != inspect.Parameter.empty 
            else "未知"
        )
        
        param_info = {
            "name": name,
            "required": param.default == inspect.Parameter.empty,
            "type": param_type
        }
        
        if param.default != inspect.Parameter.empty:
            # 防止非序列化的默认值
            try:
                param_info["default"] = param.default
            except Exception:
                param_info["default"] = str(param.default)
        
        params.append(param_info)
    
    return params 