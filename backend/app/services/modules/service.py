import os
import sys
from typing import Dict, Any, List

from ...core.config import settings


class ModuleService:
    def __init__(self):
        self.base_dir = settings.MCP_BASE_DIR
        self.modules = settings.MCP_MODULES

    def get_all_modules(self) -> Dict[str, Any]:
        """获取所有模块文件"""
        modules = {}
        
        for root, _, files in os.walk(self.base_dir):
            if "backend" in root or "frontend" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.base_dir)
                    
                    try:
                        content = self.get_module_content(rel_path)
                        modules[rel_path] = {
                            "path": rel_path,
                            "content": content,
                            "size": os.path.getsize(file_path)
                        }
                    except FileNotFoundError:
                        continue
        
        return modules

    def get_module_content(self, module_path: str) -> str:
        """获取模块内容"""
        full_path = os.path.join(self.base_dir, module_path)
        
        if not os.path.exists(full_path) or not full_path.endswith(".py"):
            raise FileNotFoundError("模块不存在")
        
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def update_module(self, module_path: str, content: str) -> None:
        """更新模块内容"""
        full_path = os.path.join(self.base_dir, module_path)
        
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

    def create_module(self, module_path: str, content: str) -> str:
        """创建新模块"""
        if not module_path.endswith(".py"):
            module_path += ".py"
        
        full_path = os.path.join(self.base_dir, module_path)
        
        if os.path.exists(full_path):
            raise FileExistsError("模块已存在")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return module_path

    def delete_module(self, module_path: str) -> None:
        """删除模块"""
        full_path = os.path.join(self.base_dir, module_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError("模块不存在")
        
        os.remove(full_path)
        
        # 从缓存中移除
        module_name = os.path.basename(full_path).replace(".py", "")
        if module_name in self.modules:
            del self.modules[module_name]
            if module_name in sys.modules:
                del sys.modules[module_name]

    def list_modules(self) -> List[str]:
        """列出所有模块"""
        modules = []
        repository_path = os.path.join(self.base_dir, "repository")
        for root, _, files in os.walk(repository_path):
            for file in files:
                if file.endswith(".py") and file != "_init_.py" and file != "__init__.py":
                    rel_path = os.path.relpath(
                        os.path.join(root, file), 
                        self.base_dir
                    )
                    modules.append(rel_path)
        return modules

    def get_module_count(self) -> int:
        """获取模块数量"""
        count = 0
        repository_path = os.path.join(self.base_dir, "repository")
        for root, _, files in os.walk(repository_path):
            for file in files:
                if file.endswith(".py") and file != "_init_.py" and file != "__init__.py":
                    count += 1
        return count 