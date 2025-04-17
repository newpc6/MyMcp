import os
import sys
import importlib.util
import inspect
from typing import Dict, Any, List

from ...core.config import settings


class ResourceService:
    def __init__(self):
        self.base_dir = settings.MCP_BASE_DIR
        self.modules = settings.MCP_MODULES

    def get_all_resources(self) -> List[Dict[str, Any]]:
        """获取所有资源信息"""
        resources = self.scan_resources()
        return list(resources.values())

    def get_resource_content(self, resource_path: str) -> str:
        """获取资源内容"""
        full_path = os.path.join(self.base_dir, resource_path)
        
        if not os.path.exists(full_path) or not full_path.endswith(".py"):
            raise FileNotFoundError("Resource not found")
        
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def update_resource(self, resource_path: str, content: str) -> None:
        """更新资源内容"""
        full_path = os.path.join(self.base_dir, resource_path)
        
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

    def create_resource(self, resource_path: str, content: str) -> str:
        """创建新资源"""
        if not resource_path.endswith(".py"):
            resource_path += ".py"
        
        full_path = os.path.join(self.base_dir, resource_path)
        
        if os.path.exists(full_path):
            raise FileExistsError("Resource already exists")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return resource_path

    def delete_resource(self, resource_path: str) -> None:
        """删除资源"""
        full_path = os.path.join(self.base_dir, resource_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError("Resource not found")
        
        os.remove(full_path)
        
        # 从缓存中移除
        module_name = os.path.basename(full_path).replace(".py", "")
        if module_name in self.modules:
            del self.modules[module_name]
            if module_name in sys.modules:
                del sys.modules[module_name]

    def scan_resources(self) -> Dict[str, Any]:
        """扫描所有MCP资源"""
        resources = {}
        
        # 获取所有Python文件
        py_files = []
        repository_path = os.path.join(self.base_dir, "repository")
        for root, _, files in os.walk(repository_path):
            for file in files:
                if file.endswith(".py") and file != "_init_.py":
                    py_files.append(os.path.join(root, file))
        
        # 添加必要的目录到sys.path
        if repository_path not in sys.path:
            sys.path.insert(0, repository_path)
        if self.base_dir not in sys.path:
            sys.path.insert(0, self.base_dir)
        
        # 首先导入mcp_base
        try:
            import repository.mcp_base  # noqa: F401
        except ImportError as e:
            print(f"导入mcp_base失败: {e}")
            return resources
        
        # 加载所有模块并扫描资源
        for py_file in py_files:
            module_name = os.path.basename(py_file).replace(".py", "")
            if module_name == "mcp_base":
                continue
            
            if module_name in self.modules:
                module = self.modules[module_name]
            else:
                try:
                    # 动态加载模块
                    spec = importlib.util.spec_from_file_location(
                        module_name, py_file
                    )
                    if not spec or not spec.loader:
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    self.modules[module_name] = module
                except Exception as e:
                    print(f"加载模块 {module_name} 时出错: {str(e)}")
                    continue
            
            # 查找所有被装饰为MCP资源的函数
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj):
                    if (hasattr(obj, "__mcp_resource__") and 
                            obj.__mcp_resource__):
                        sig = inspect.signature(obj)
                        resources[obj.__mcp_resource_path__] = {
                            "path": obj.__mcp_resource_path__,
                            "doc": obj.__doc__ or "",
                            "return_type": str(sig.return_annotation),
                            "module": module_name,
                            "file_path": py_file
                        }
        
        return resources

    def get_resource_info(self, resource_path: str) -> Dict[str, Any]:
        """获取特定资源的信息"""
        resources = self.scan_resources()
        if resource_path not in resources:
            raise ValueError(f"资源 {resource_path} 不存在")
        return resources[resource_path]

    def list_resources(self) -> List[str]:
        """列出所有可用的资源路径"""
        resources = self.scan_resources()
        return list(resources.keys()) 