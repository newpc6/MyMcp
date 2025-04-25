"""
工具执行相关API
"""
import importlib
import sys
import tempfile
import os
from starlette.routing import Route
from starlette.requests import Request

from app.utils.response import success_response, error_response
from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpTool, McpModule
from app.services.execution.executor import execute_tool_by_name


async def execute_tool(request: Request):
    """
    执行指定工具
    
    Args:
        tool_name: 工具名称
        params: 工具参数
    """
    tool_name = request.path_params["tool_name"]
    params = await request.json()
    
    try:
        result = await execute_tool_by_name(tool_name, params)
        if "error" in result:
            return error_response(result["error"], code=400, http_status_code=400)
        return success_response({"result": result})
    except Exception as e:
        return error_response(f"执行失败: {str(e)}", code=500, http_status_code=500)


async def execute_tool_by_id(request: Request):
    """
    根据ID执行MCP工具
    
    Args:
        tool_id: 工具ID
        params: 工具参数
    """
    tool_id = int(request.path_params["tool_id"])
    params = await request.json()
    
    try:
        with get_db() as db:
            # 从数据库获取工具信息
            tool = db.query(McpTool).filter(McpTool.id == tool_id).first()
            if not tool:
                return error_response("工具不存在", code=404, http_status_code=404)
            
            # 获取模块和函数名
            module_path = tool.module.module_path
            function_name = tool.function_name
            
            # 动态导入模块
            module = importlib.import_module(module_path)
            # 获取函数对象
            func = getattr(module, function_name)
            
            # 执行函数
            result = func(**params)
            
            # 返回结果
            return success_response({"result": result})
    except Exception as e:
        return error_response(f"执行失败: {str(e)}", code=500, http_status_code=500)


async def execute_module_function(request: Request):
    """
    根据模块ID和函数名执行工具
    
    Args:
        module_id: 模块ID
        function_name: 函数名
        params: 工具参数
    """
    module_id = int(request.path_params["module_id"])
    function_name = request.path_params["function_name"]
    params = await request.json()
    
    try:
        with get_db() as db:
            # 从数据库获取模块信息
            module = db.query(McpModule).filter(McpModule.id == module_id).first()
            if not module:
                return error_response("模块不存在", code=404, http_status_code=404)
            
            if not module.code:
                return error_response("模块代码为空", code=400, http_status_code=400)
            
            # 创建临时目录和文件
            temp_dir = tempfile.mkdtemp(prefix="mcp_exec_")
            temp_file = os.path.join(temp_dir, f"{module.name}.py")
            
            try:
                # 写入模块代码到临时文件
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(module.code)
                
                # 将临时目录添加到Python路径
                if temp_dir not in sys.path:
                    sys.path.insert(0, temp_dir)
                
                # 动态导入模块
                module_name = module.name
                spec = importlib.util.find_spec(module_name)
                if not spec:
                    return error_response("无法加载模块", code=500, http_status_code=500)
                
                imported_module = importlib.import_module(module_name)
                
                # 检查函数是否存在
                if not hasattr(imported_module, function_name):
                    return error_response(
                        f"函数 {function_name} 不存在", 
                        code=404, 
                        http_status_code=404
                    )
                
                # 获取函数对象
                func = getattr(imported_module, function_name)
                
                # 执行函数
                result = func(**params)
                
                # 返回结果
                return success_response({"result": result})
            
            finally:
                # 清理临时文件和目录
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    pass  # 忽略清理错误
                
                # 从Python路径中移除临时目录
                if temp_dir in sys.path:
                    sys.path.remove(temp_dir)
                
    except Exception as e:
        import traceback
        return error_response(
            f"执行失败: {str(e)}", 
            data={"traceback": traceback.format_exc()},
            code=500, 
            http_status_code=500
        )


def get_router():
    """获取工具执行路由"""
    routes = [
        Route("/{tool_name}", endpoint=execute_tool, methods=["POST"]),
        Route("/tool/{tool_id}", endpoint=execute_tool_by_id, methods=["POST"]),
        Route("/module/{module_id}/function/{function_name}", endpoint=execute_module_function, methods=["POST"])
    ]
    
    return routes