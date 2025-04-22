from typing import List, Dict, Any, Optional

from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpModule, McpTool
from app.services.repository.repository_manager import get_repository_tools


class MarketplaceService:
    """MCP广场服务"""

    def list_modules(self) -> List[Dict[str, Any]]:
        """获取所有MCP模块列表"""
        with get_db() as db:
            modules = db.query(McpModule).all()
            return [module.to_dict() for module in modules]

    def get_module(self, module_id: int) -> Optional[Dict[str, Any]]:
        """获取指定MCP模块详情"""
        with get_db() as db:
            query = db.query(McpModule)
            module = query.filter(McpModule.id == module_id).first()
            return module.to_dict() if module else None

    def get_module_tools(
        self, 
        module_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        """获取指定MCP模块的所有工具"""
        with get_db() as db:
            # 检查模块是否存在
            query = db.query(McpModule)
            module = query.filter(McpModule.id == module_id).first()
            if not module:
                return None
            
            query = db.query(McpTool)
            tools = query.filter(McpTool.module_id == module_id).all()
            return [tool.to_dict() for tool in tools]

    def get_tool(self, tool_id: int) -> Optional[Dict[str, Any]]:
        """获取指定MCP工具详情"""
        with get_db() as db:
            tool = db.query(McpTool).filter(McpTool.id == tool_id).first()
            return tool.to_dict() if tool else None

    def scan_repository_modules(self) -> Dict[str, int]:
        """扫描仓库中的MCP模块并更新数据库"""
        # 获取repository目录中的所有工具
        repo_tools = get_repository_tools()
        result = {
            "total": 0,
            "new_modules": 0,
            "updated_modules": 0,
            "new_tools": 0,
            "updated_tools": 0
        }
        
        # 按照模块分组整理工具
        modules_dict = {}
        for tool_info in repo_tools:
            module_path = tool_info["module_path"]
            if module_path not in modules_dict:
                modules_dict[module_path] = {
                    "module_path": module_path,
                    "name": module_path.split(".")[-1],
                    "tools": []
                }
            modules_dict[module_path]["tools"].append(tool_info)
        
        with get_db() as db:
            # 更新或创建模块和工具
            for module_path, module_info in modules_dict.items():
                # 检查模块是否已存在
                module = db.query(McpModule).filter(
                    McpModule.module_path == module_path
                ).first()
                
                if module is None:
                    # 创建新模块
                    module = McpModule(
                        name=module_info["name"],
                        module_path=module_path,
                        description=f"{module_info['name']} 模块",
                        is_hosted=False
                    )
                    db.add(module)
                    db.flush()
                    result["new_modules"] += 1
                else:
                    result["updated_modules"] += 1
                
                # 处理模块中的工具
                for tool_info in module_info["tools"]:
                    tool = db.query(McpTool).filter(
                        McpTool.module_id == module.id,
                        McpTool.function_name == tool_info["function_name"]
                    ).first()
                    
                    if tool is None:
                        # 创建新工具
                        tool = McpTool(
                            module_id=module.id,
                            name=tool_info["function_name"],
                            function_name=tool_info["function_name"],
                            description=tool_info["description"],
                            parameters="{}",  # 默认空参数定义
                            is_enabled=True
                        )
                        db.add(tool)
                        result["new_tools"] += 1
                    else:
                        # 更新工具信息
                        tool.description = tool_info["description"]
                        result["updated_tools"] += 1
            
            result["total"] = len(repo_tools)
            db.commit()
            return result


# 单例模式
marketplace_service = MarketplaceService() 