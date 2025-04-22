"""
MCP广场服务
"""
from typing import List, Dict, Any, Optional
import os
import sys
import inspect
import importlib.util
import importlib
import tempfile

from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError

from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpModule, McpTool, McpCategory
from app.core.utils import now_beijing
from app.utils.logging import em_logger


class MarketplaceService:
    """MCP广场服务"""
    
    def list_modules(
        self, category_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取MCP模块列表"""
        with get_db() as db:
            query = select(McpModule)
            
            # 如果指定了分组ID，按分组过滤
            if category_id:
                query = query.where(McpModule.category_id == category_id)
                
            modules = db.execute(query).scalars().all()
            return [m.to_dict() for m in modules]
    
    def get_module(self, module_id: int) -> Optional[Dict[str, Any]]:
        """获取指定的MCP模块信息"""
        with get_db() as db:
            query = select(McpModule).where(McpModule.id == module_id)
            module = db.execute(query).scalar_one_or_none()
            if module:
                return module.to_dict()
            return None
    
    def get_module_tools(
        self, module_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        """获取指定MCP模块的所有工具"""
        with get_db() as db:
            # 先检查模块是否存在
            module_query = select(McpModule).where(McpModule.id == module_id)
            module = db.execute(module_query).scalar_one_or_none()
            if not module:
                return None
            
            # 获取该模块下的所有工具
            query = select(McpTool).where(McpTool.module_id == module_id)
            tools = db.execute(query).scalars().all()
            return [t.to_dict() for t in tools]
    
    def get_tool(self, tool_id: int) -> Optional[Dict[str, Any]]:
        """获取指定MCP工具的详情"""
        with get_db() as db:
            query = select(McpTool).where(McpTool.id == tool_id)
            tool = db.execute(query).scalar_one_or_none()
            if tool:
                return tool.to_dict()
            return None
    
    def scan_repository_modules(self) -> Dict[str, int]:
        """扫描数据库中的MCP模块并更新工具信息"""
        # 结果统计
        stats = {
            "total": 0,      # 总共扫描的模块数
            "updated": 0,    # 更新工具的模块数
            "tools": 0       # 扫描到的工具数
        }
        
        try:
            with get_db() as db:
                # 查询所有模块
                modules = db.execute(select(McpModule)).scalars().all()
                stats["total"] = len(modules)
                
                if not modules:
                    em_logger.warning("数据库中没有找到MCP模块")
                    return stats
                
                em_logger.info(f"在数据库中找到{len(modules)}个MCP模块")
                
                # 创建临时目录存放模块代码
                temp_dir = tempfile.mkdtemp(prefix="mcp_modules_")
                
                # 添加临时目录到Python路径
                if temp_dir not in sys.path:
                    sys.path.insert(0, temp_dir)
                
                # 处理每个模块
                for module in modules:
                    if not module.code:
                        em_logger.warning(f"模块 {module.name} 没有代码内容，跳过")
                        continue
                    
                    # 创建临时模块文件
                    module_file = os.path.join(temp_dir, f"{module.name}.py")
                    
                    try:
                        # 写入代码到临时文件
                        with open(module_file, "w", encoding="utf-8") as f:
                            f.write(module.code)
                        
                        # 动态导入模块
                        module_name = module.name
                        
                        spec = importlib.util.spec_from_file_location(
                            module_name, module_file
                        )
                        if spec and spec.loader:
                            module_obj = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module_obj)
                            
                            # 扫描模块中的函数
                            tool_count = self._scan_module_tools(
                                db, module_obj, module.id, module_name
                            )
                            
                            if tool_count > 0:
                                stats["updated"] += 1
                                stats["tools"] += tool_count
                                
                    except Exception as e:
                        em_logger.error(
                            f"处理模块 {module.name} 失败: {str(e)}"
                        )
                
                # 清理临时目录
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    em_logger.warning(f"清理临时目录失败: {str(e)}")
                
                db.commit()
                return stats
                
        except Exception as e:
            em_logger.error(f"扫描模块时出错: {str(e)}")
            return stats
    
    def _scan_module_tools(
        self, db, module_obj, module_id: int, module_name: str
    ) -> int:
        """扫描模块中的函数作为工具"""
        tool_count = 0
        
        for func_name, func in inspect.getmembers(module_obj, inspect.isfunction):
            # 过滤出该模块定义的函数(而不是导入的函数)
            if func.__module__ == module_name:
                # 获取函数文档和参数信息
                doc = inspect.getdoc(func) or f"{func_name} 函数"
                signature = inspect.signature(func)
                parameters = {}
                
                for param_name, param in signature.parameters.items():
                    if param_name == 'self':  # 跳过self参数
                        continue
                        
                    param_type = "any"
                    if param.annotation != param.empty:
                        param_type = str(param.annotation)
                    
                    param_info = {
                        "type": param_type,
                        "required": param.default == param.empty
                    }
                    
                    if param.default != param.empty:
                        param_info["default"] = param.default
                        
                    parameters[param_name] = param_info
                
                # 查询该工具是否已存在
                query_conditions = [
                    McpTool.module_id == module_id,
                    McpTool.function_name == func_name
                ]
                tool_query = select(McpTool).where(*query_conditions)
                
                # 获取现有工具
                existing_tool = db.execute(
                    tool_query
                ).scalar_one_or_none()
                
                if existing_tool:
                    # 更新现有工具
                    stmt = (
                        update(McpTool)
                        .where(McpTool.id == existing_tool.id)
                        .values(
                            name=func_name,
                            description=doc,
                            parameters=str(parameters) if parameters else None,
                            updated_at=now_beijing()
                        )
                    )
                    db.execute(stmt)
                else:
                    # 创建新工具
                    new_tool = McpTool(
                        module_id=module_id,
                        name=func_name,
                        function_name=func_name,
                        description=doc,
                        parameters=str(parameters) if parameters else None,
                        created_at=now_beijing(),
                        updated_at=now_beijing(),
                        is_enabled=True
                    )
                    db.add(new_tool)
                
                tool_count += 1
                
        return tool_count
    
    def list_categories(self) -> List[Dict[str, Any]]:
        """获取所有MCP分组"""
        with get_db() as db:
            query = select(McpCategory).order_by(McpCategory.order)
            categories = db.execute(query).scalars().all()
            return [c.to_dict() for c in categories]
    
    def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        """获取指定MCP分组详情"""
        with get_db() as db:
            query = select(McpCategory).where(McpCategory.id == category_id)
            category = db.execute(query).scalar_one_or_none()
            if category:
                return category.to_dict()
            return None
    
    def create_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建MCP分组"""
        with get_db() as db:
            # 获取最大排序号
            max_order_query = select(McpCategory).order_by(
                McpCategory.order.desc()
            )
            max_order_category = db.execute(
                max_order_query
            ).scalar_one_or_none()
            if max_order_category:
                max_order = max_order_category.order + 10
            else:
                max_order = 0
            
            # 创建新分组
            category = McpCategory(
                name=data["name"],
                description=data.get("description"),
                icon=data.get("icon"),
                order=data.get("order", max_order),
                created_at=now_beijing(),
                updated_at=now_beijing()
            )
            
            db.add(category)
            db.commit()
            db.refresh(category)
            
            return category.to_dict()
    
    def update_category(
        self, category_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新MCP分组"""
        with get_db() as db:
            # 检查分组是否存在
            category_query = select(McpCategory).where(
                McpCategory.id == category_id
            )
            category = db.execute(category_query).scalar_one_or_none()
            if not category:
                return None
            
            # 更新分组信息
            update_data = {}
            if "name" in data:
                update_data["name"] = data["name"]
            if "description" in data:
                update_data["description"] = data["description"]
            if "icon" in data:
                update_data["icon"] = data["icon"]
            if "order" in data:
                update_data["order"] = data["order"]
                
            update_data["updated_at"] = now_beijing()
            
            stmt = (
                update(McpCategory)
                .where(McpCategory.id == category_id)
                .values(**update_data)
            )
            db.execute(stmt)
            db.commit()
            
            # 返回更新后的分组信息
            updated_category = db.execute(category_query).scalar_one()
            return updated_category.to_dict()
    
    def delete_category(self, category_id: int) -> bool:
        """删除MCP分组"""
        with get_db() as db:
            try:
                # 检查分组是否存在
                category_query = select(McpCategory).where(
                    McpCategory.id == category_id
                )
                category = db.execute(category_query).scalar_one_or_none()
                if not category:
                    return False
                
                # 先将该分组下的模块解除关联
                stmt = (
                    update(McpModule)
                    .where(McpModule.category_id == category_id)
                    .values(category_id=None)
                )
                db.execute(stmt)
                
                # 删除分组
                stmt = delete(McpCategory).where(McpCategory.id == category_id)
                db.execute(stmt)
                db.commit()
                return True
            except SQLAlchemyError as e:
                em_logger.error(f"删除分组失败: {str(e)}")
                db.rollback()
                return False
    
    def update_module_category(
        self, module_id: int, category_id: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """更新模块所属分组"""
        with get_db() as db:
            # 检查模块是否存在
            module_query = select(McpModule).where(McpModule.id == module_id)
            module = db.execute(module_query).scalar_one_or_none()
            if not module:
                return None
                
            # 如果提供了分组ID，检查分组是否存在
            if category_id is not None:
                category_query = select(McpCategory).where(
                    McpCategory.id == category_id
                )
                category = db.execute(category_query).scalar_one_or_none()
                if not category:
                    return None
            
            # 更新模块分组关联
            stmt = (
                update(McpModule)
                .where(McpModule.id == module_id)
                .values(category_id=category_id, updated_at=now_beijing())
            )
            db.execute(stmt)
            db.commit()
            
            # 返回更新后的模块信息
            updated_module = db.execute(module_query).scalar_one()
            return updated_module.to_dict()

    def create_module(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建MCP模块"""
        with get_db() as db:
            # 创建模块记录
            module = McpModule(
                name=data.get("name"),
                description=data.get("description", ""),
                module_path=f"repository.{data.get('name')}",
                author=data.get("author", "系统创建"),
                version=data.get("version", "1.0.0"),
                tags=",".join(data.get("tags", [])),
                icon=data.get("icon", ""),
                is_hosted=True,  # 使用数据库存储的模块默认为托管模块
                repository_url=data.get("repository_url", ""),
                category_id=data.get("category_id"),
                code=data.get("code", ""),
                config_schema=data.get("config_schema", "{}"),
                created_at=now_beijing(),
                updated_at=now_beijing()
            )
            
            db.add(module)
            db.commit()
            db.refresh(module)
            
            return module.to_dict()
    
    def update_module(
        self, module_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新MCP模块"""
        with get_db() as db:
            try:
                # 查询模块是否存在
                query = select(McpModule).where(McpModule.id == module_id)
                module = db.execute(query).scalar_one_or_none()
                
                if not module:
                    return None
                
                # 更新字段
                update_data = {
                    "updated_at": now_beijing()
                }
                
                if "name" in data:
                    update_data["name"] = data["name"]
                if "description" in data:
                    update_data["description"] = data["description"]
                if "module_path" in data:
                    update_data["module_path"] = data["module_path"]
                if "author" in data:
                    update_data["author"] = data["author"]
                if "version" in data:
                    update_data["version"] = data["version"]
                if "tags" in data:
                    # 如果是列表，则转换为逗号分隔的字符串
                    if isinstance(data["tags"], list):
                        update_data["tags"] = ",".join(data["tags"])
                    else:
                        update_data["tags"] = data["tags"]
                if "icon" in data:
                    update_data["icon"] = data["icon"]
                if "is_hosted" in data:
                    update_data["is_hosted"] = data["is_hosted"]
                if "repository_url" in data:
                    update_data["repository_url"] = data["repository_url"]
                if "code" in data:
                    update_data["code"] = data["code"]
                if "config_schema" in data:
                    update_data["config_schema"] = data["config_schema"]
                if "markdown_docs" in data:
                    update_data["markdown_docs"] = data["markdown_docs"]
                
                # 更新数据库
                stmt = (
                    update(McpModule)
                    .where(McpModule.id == module_id)
                    .values(**update_data)
                )
                db.execute(stmt)
                db.commit()
                
                # 返回更新后的模块信息
                return self.get_module(module_id)
                
            except SQLAlchemyError as e:
                em_logger.error(f"更新模块失败: {str(e)}")
                db.rollback()
                return None
    
    def delete_module(self, module_id: int) -> bool:
        """删除MCP模块"""
        with get_db() as db:
            try:
                # 检查模块是否存在
                module_query = select(McpModule).where(
                    McpModule.id == module_id
                )
                module = db.execute(module_query).scalar_one_or_none()
                if not module:
                    return False
                
                # 删除模块记录（关联的工具会通过级联关系自动删除）
                stmt = delete(McpModule).where(McpModule.id == module_id)
                db.execute(stmt)
                db.commit()
                return True
            except SQLAlchemyError as e:
                em_logger.error(f"删除模块失败: {str(e)}")
                db.rollback()
                return False


# 创建服务实例
marketplace_service = MarketplaceService() 