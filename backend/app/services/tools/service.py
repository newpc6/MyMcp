import os
import sys
import importlib.util
import inspect
import time
from typing import Dict, Any, List

# 导入MCP服务器实例
from ...server.mcp_server import server_instance
from ...core.config import settings
from ...models.tools.schemas import ToolContent
# 导入历史服务
from ..history.service import HistoryService

# 创建历史服务实例
history_service = HistoryService()


class ToolService:
    def __init__(self):
        self.base_dir = settings.MCP_BASE_DIR
        self.modules = settings.MCP_MODULES
        # 缓存已注册的工具名称 (使用内部属性，注意风险)
        try:
            self._registered_tool_names = {
                tool.name for tool in server_instance._tool_manager.list_tools()
            } if server_instance else set()
        except Exception as e:
            print(f"初始化时无法从server_instance._tool_manager获取工具列表: {e}")
            self._registered_tool_names = set()

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具信息"""
        # 每次调用都重新扫描，以反映文件系统变化（如手动添加/删除文件）
        # 并尝试更新已注册工具列表缓存
        try:
            self._registered_tool_names = {
                tool.name for tool in server_instance._tool_manager.list_tools()
            } if server_instance else set()
        except Exception as e:
            print(f"更新时无法从server_instance._tool_manager获取工具列表: {e}")
            # 保留旧缓存或清空？这里选择保留旧缓存
            # self._registered_tool_names = set()

        tools = self.scan_tools()
        return list(tools.values())

    def get_tool_content(self, tool_path: str) -> ToolContent:
        """获取工具内容"""
        full_path = os.path.join(self.base_dir, tool_path)
        
        if not os.path.exists(full_path) or not full_path.endswith(".py"):
            raise FileNotFoundError("Tool not found")
        
        with open(full_path, "r", encoding="utf-8") as f:
            return {"content": f.read()}

    def update_tool(self, tool_path: str, content: str) -> None:
        """更新工具内容"""
        full_path = os.path.join(self.base_dir, tool_path)
        
        if not full_path.endswith(".py"):
            raise ValueError("只能编辑Python文件")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 重新加载模块
        module_name = os.path.basename(full_path).replace(".py", "")
        if module_name in self.modules:
            del self.modules[module_name]
            if module_name in sys.modules:
                del sys.modules[module_name]

    def create_tool(self, tool_path: str, content: str) -> str:
        """创建新工具"""
        if not tool_path.endswith(".py"):
            tool_path += ".py"
        
        full_path = os.path.join(self.base_dir, tool_path)
        
        if os.path.exists(full_path):
            raise FileExistsError("Tool already exists")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return tool_path

    def delete_tool(self, tool_path: str) -> None:
        """删除工具"""
        full_path = os.path.join(self.base_dir, tool_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError("Tool not found")
        
        os.remove(full_path)
        
        # 从缓存中移除
        module_name = os.path.basename(full_path).replace(".py", "")
        if module_name in self.modules:
            del self.modules[module_name]
            if module_name in sys.modules:
                del sys.modules[module_name]

    def scan_tools(self) -> Dict[str, Any]:
        """扫描所有MCP工具"""
        tools = {}
        
        # 每次扫描都实时获取最新的工具列表，不依赖于缓存
        try:
            if server_instance and hasattr(server_instance, '_tool_manager'):
                registered_tools = server_instance._tool_manager.list_tools()
                registered_tool_names = {tool.name for tool in registered_tools}
                print(f"从server_instance._tool_manager获取到的工具列表: {registered_tool_names}")
                if not registered_tool_names:
                    print("警告: server_instance._tool_manager中没有找到任何注册工具！")
            else:
                print("警告: server_instance不存在或未初始化")
                registered_tool_names = set()
        except Exception as e:
            print(f"获取已注册工具列表时出错: {e}")
            registered_tool_names = set()
        
        # 更新实例变量，以便其他方法使用
        self._registered_tool_names = registered_tool_names

        # 获取所有Python文件
        py_files = []
        repository_path = os.path.join(self.base_dir, "repository")
        for root, _, files in os.walk(repository_path):
            for file in files:
                if (file.endswith(".py") and file != "_init_.py" and 
                    file != "__init__.py"):
                    py_files.append(os.path.join(root, file))
        
        print(f"找到{len(py_files)}个Python文件")
        
        # 添加必要的目录到sys.path
        if repository_path not in sys.path:
            sys.path.insert(0, repository_path)
        if self.base_dir not in sys.path:
            sys.path.insert(0, self.base_dir)
        
        # 加载所有模块并扫描工具
        for py_file in py_files:
            module_rel_path = os.path.relpath(py_file, repository_path)
            module_dot_path = module_rel_path.replace(
                os.sep, "."
            ).replace(".py", "")
            module_key = f"repository.{module_dot_path}"
            
            if module_key == "repository.mcp_base":
                # 跳过已移除的mcp_base文件
                continue
            
            print(f"处理模块: {module_key}")
            
            # 加载模块
            module = None
            try:
                spec = importlib.util.spec_from_file_location(
                    module_key, py_file
                )
                if not spec or not spec.loader:
                    continue
                
                if module_key in sys.modules:
                    module = sys.modules[module_key]
                else:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_key] = module
                    spec.loader.exec_module(module)
            except Exception as e:
                print(f"加载模块 {module_key} 时出错: {e}")
                continue
            
            if module is None:
                continue
            
            # 查找所有函数，检查是否在注册工具列表中
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj):
                    if obj.__name__ in registered_tool_names:
                        print(f"✓ 在模块 {module_key} 中找到已注册工具: {obj.__name__}")
                        sig = inspect.signature(obj)
                        param_info = {}
                        
                        for param_name, param in sig.parameters.items():
                            param_type_str = str(param.annotation)
                            if hasattr(param.annotation, '__name__'):
                                param_type_str = param.annotation.__name__
                            elif hasattr(param.annotation, '__origin__'):
                                origin_name = getattr(
                                    param.annotation.__origin__, 
                                    '__name__', 
                                    str(param.annotation.__origin__)
                                )
                                args_str = ", ".join(
                                    getattr(arg, '__name__', str(arg)) 
                                    for arg in getattr(
                                        param.annotation, '__args__', []
                                    )
                                )
                                param_type_str = f"{origin_name}[{args_str}]"
                            
                            param_info[param_name] = {
                                "type": param_type_str 
                                    if param_type_str != '_empty' else 'Any',
                                "default": repr(param.default) 
                                    if param.default is not inspect.Parameter.empty
                                    else None
                            }
                        
                        # 使用相对于 base_dir 的路径
                        relative_file_path = os.path.relpath(
                            py_file, self.base_dir
                        )
                        
                        tools[obj.__name__] = {
                            "name": obj.__name__,
                            "doc": inspect.getdoc(obj) or "",
                            "parameters": param_info,
                            "return_type": (
                                str(sig.return_annotation)
                                if str(sig.return_annotation) != '_empty' 
                                else 'Any'
                            ),
                            "module": module_key,
                            "file_path": relative_file_path.replace("\\", "/")
                        }
                    else:
                        # 额外打印未注册的函数，帮助诊断
                        print(
                            f"× 模块 {module_key} 中的函数 {obj.__name__} "
                            f"未在工具管理器中注册"
                        )
        
        print(f"扫描完成，找到已注册工具: {list(tools.keys())}")
        return tools

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """执行MCP工具"""
        start_time = time.time()
        result = None
        status = "success"
        
        try:
            # 获取工具信息
            tools = self.scan_tools()
            description = tools.get(tool_name, {}).get("doc", "")
            
            if not server_instance:
                raise ValueError("MCP服务器实例未初始化")
                
            # 获取工具函数对象
            tool_info = server_instance._tool_manager._tools.get(tool_name)
            if not tool_info:
                raise ValueError(f"工具 {tool_name} 未在 ToolManager 中注册")

            # 直接执行工具函数
            result = tool_info.fn(**parameters)
            return result
        except Exception as e:
            # 更详细的错误信息
            import traceback
            status = "failed"
            error_msg = f"执行工具 {tool_name} 时出错: {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            raise RuntimeError(error_msg)
        finally:
            # 计算执行时间（毫秒）
            execution_time = int((time.time() - start_time) * 1000)
            
            # 记录执行历史
            try:
                history_service.record_tool_execution(
                    tool_name=tool_name,
                    description=(
                        description if 'description' in locals() else ""
                    ),
                    parameters=parameters,
                    result=result,
                    status=status,
                    execution_time=execution_time
                )
            except Exception as e:
                print(f"记录工具执行历史失败: {e}")


    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """获取特定工具的信息"""
        try:
            if not server_instance:
                raise ValueError("MCP服务器实例未初始化")
                
            # 直接从内部工具注册表获取
            tool_info = server_instance._tool_manager._tools.get(tool_name)
            if not tool_info:
                raise ValueError(f"工具 {tool_name} 未在 ToolManager 中注册")
            
            # 构建工具信息
            sig = inspect.signature(tool_info.fn)
            param_info = {}
            
            # 获取参数信息
            for param_name, param in sig.parameters.items():
                param_type_str = str(param.annotation)
                if param_type_str == '_empty':
                    param_type_str = 'Any'
                    
                param_info[param_name] = {
                    "type": param_type_str,
                    "default": (
                        repr(param.default) 
                        if param.default is not inspect.Parameter.empty 
                        else None
                    )
                }
            
            # 获取文件路径（相对于 base_dir）
            file_path = inspect.getfile(tool_info.fn)
            if self.base_dir in file_path:
                relative_path = os.path.relpath(file_path, self.base_dir)
            else:
                relative_path = file_path
                
            return {
                "name": tool_info.name,
                "doc": (
                    tool_info.description or 
                    inspect.getdoc(tool_info.fn) or ""
                ),
                "parameters": param_info,
                "return_type": (
                    str(sig.return_annotation) 
                    if str(sig.return_annotation) != '_empty' 
                    else 'Any'
                ),
                "module": getattr(
                    inspect.getmodule(tool_info.fn), '__name__', '未知模块'
                ),
                "file_path": relative_path.replace("\\", "/")
            }
        except Exception as e:
            print(f"获取工具信息 {tool_name} 时出错: {e}")
            raise ValueError(f"无法获取工具 {tool_name} 的信息: {str(e)}")


    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有可用的工具信息，按模块分组"""
        # 直接调用scan_tools获取最新工具列表
        try:
            tools = self.scan_tools()
            
            # 按模块分组工具
            modules_dict = {}
            for tool_name, tool_info in tools.items():
                module_name = tool_info["module"]
                if module_name not in modules_dict:
                    modules_dict[module_name] = {
                        "module_name": module_name,
                        "tools": []
                    }
                modules_dict[module_name]["tools"].append(tool_info)
            
            # 将字典转为列表
            module_list = list(modules_dict.values())
            
            # 对每个模块内的工具按名称排序
            for module in module_list:
                module["tools"].sort(key=lambda x: x["name"])
            
            # 对模块列表按模块名排序
            module_list.sort(key=lambda x: x["module_name"])
            
            print(
                f"list_tools返回模块列表: "
                f"{[module['module_name'] for module in module_list]}"
            )
            return module_list
        except Exception as e:
            import traceback
            print(f"列出工具时出错: {e}\n{traceback.format_exc()}")
            return [] 