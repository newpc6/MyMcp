"""
MCP广场服务
"""
from datetime import datetime
import json
from typing import List, Dict, Any, Optional
import os
import sys
import inspect
import importlib.util
import importlib
import tempfile

from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError

from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpModule, McpTool
from app.core.utils import now_beijing
from app.utils.logging import mcp_logger
from app.services.mcp_service.service_manager import service_manager
from app.utils.permissions import add_edit_permission
from app.models.group.group import McpGroup
from app.utils.http.pagination import PageParams
from app.utils.http.utils import build_page_response


class MarketplaceService:
    """MCP广场服务"""
    
    def page_modules(
        self, 
        page_params: PageParams,
        user_id: Optional[int] = None, 
        is_admin: bool = False,
        condition: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """获取MCP模块列表（分页）
        
        参数:
            page_params: 分页参数
            category_id: 分类ID，可选
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户
            
        返回:
            分页结果
        """
        with get_db() as db:
            query = select(McpModule)
            
            # 如果指定了分组ID，按分组过滤
            if condition.get("category_id"):
                if condition.get("category_id") == "all":
                    pass
                else:
                    query = query.where(McpModule.category_id == condition.get("category_id"))
            
            # 非管理员用户只能看到自己创建的和公开的模块
            if not is_admin and user_id is not None:
                query = query.where(
                    (McpModule.is_public == True) |
                    (McpModule.user_id == user_id)
                )
            elif not is_admin:
                # 未登录用户只能看到公开模块
                query = query.where(McpModule.is_public == True)
            
            # 获取总数
            total_count = db.execute(
                select(func.count()).select_from(query.subquery())
            ).scalar()
            
            # 分页查询，按更新时间倒序排列
            modules = db.execute(
                query.order_by(McpModule.updated_at.desc())
                .offset(page_params.offset)
                .limit(page_params.size)
            ).scalars().all()
            
            # 获取分组信息
            mcp_groups_ids = [
                m.category_id for m in modules if m.category_id
            ]
            groups = {}
            if mcp_groups_ids:
                group_list = db.execute(
                    select(McpGroup).where(
                        McpGroup.id.in_(mcp_groups_ids)
                    )
                ).scalars().all()
                groups = {g.id: g for g in group_list}
            
            # 转换为字典并添加编辑权限
            result_items = [m.to_dict(groups) for m in modules]
            result_items = add_edit_permission(
                result_items, user_id, is_admin
            )
            
            return build_page_response(
                result_items,
                total_count,
                page_params
            )
    
    def list_modules(
        self, category_id: Optional[int] = None, 
        user_id: Optional[int] = None, 
        is_admin: bool = False
    ) -> List[Dict[str, Any]]:
        """获取MCP模块列表
        
        参数:
            category_id: 分类ID，可选
            user_id: 当前用户ID，可选
            is_admin: 是否为管理员用户
            
        返回:
            MCP模块列表
        """
        with get_db() as db:
            query = select(McpModule)
            
            # 如果指定了分组ID，按分组过滤
            if category_id:
                query = query.where(McpModule.category_id == category_id)
            
            # 非管理员用户只能看到自己创建的和公开的模块
            if not is_admin and user_id is not None:
                query = query.where(
                    (McpModule.is_public is True) |
                    (McpModule.user_id == user_id)
                )
                
            modules = db.execute(query).scalars().all()
            mcp_groups_ids = [m.category_id for m in modules]
            groups = db.execute(
                select(McpGroup).where(
                    McpGroup.id.in_(mcp_groups_ids)
                )
            ).scalars().all()
            mcp_groups = {g.id: g for g in groups}
            result = [m.to_dict(mcp_groups) for m in modules]
            # 添加可编辑字段
            return add_edit_permission(result, user_id, is_admin)
    
    def get_module(self, module_id: int, user_id: Optional[int] = None, 
                  is_admin: bool = False) -> Optional[Dict[str, Any]]:
        """获取指定的MCP模块信息"""
        with get_db() as db:
            query = select(McpModule).where(McpModule.id == module_id)
            module = db.execute(query).scalar_one_or_none()
            
            if not module:
                return None
                
            # 检查权限：非管理员只能查看公开模块或自己创建的模块
            if not is_admin and user_id is not None:
                if not module.is_public and module.user_id != user_id:
                    return None
            
            group = db.execute(select(McpGroup).where(McpGroup.id == module.category_id)).scalar_one_or_none()
            if group:
                groups = {group.id: group}
            else:
                groups = {}
            result = module.to_dict(groups)
            # 添加可编辑字段
            return add_edit_permission(result, user_id, is_admin)
    
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
            
            # 如果模块没有代码，则返回空列表
            if not module.code:
                return []
            
            # 从模块代码中解析工具
            tools = []
            try:
                # 创建临时模块
                import sys
                import importlib.util
                import inspect
                import tempfile
                import os
                # 创建当天日期文件夹
                today = datetime.now().strftime("%Y-%m-%d")
                publish_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'script', 'publish', today)
                if not os.path.exists(publish_dir):
                    os.makedirs(publish_dir)
                
                code = module.code
                if code.find("${") != -1:
                    service = service_manager.get_service_by_module_id(module_id)
                    if service.config_params and code:
                        config_params = None
                        if isinstance(service.config_params, str):
                            config_params = json.loads(service.config_params)
                        else:
                            config_params = service.config_params
                        code = service_manager.replace_config_params(code, config_params)
                
                # 创建临时文件并写入代码
                with tempfile.NamedTemporaryFile(suffix='.py', prefix=f'module_{module_id}_', delete=False, dir=publish_dir) as temp:
                    temp_path = temp.name
                    temp.write(code.encode('utf-8'))
                
                try:
                    # 动态加载模块
                    module_name = f"temp_module_{module_id}"
                    spec = importlib.util.spec_from_file_location(module_name, temp_path)
                    if not spec or not spec.loader:
                        return []
                    
                    temp_module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = temp_module
                    spec.loader.exec_module(temp_module)
                    
                    # 查找所有函数
                    for name, obj in inspect.getmembers(temp_module):
                        if inspect.isfunction(obj):
                            # 解析函数签名
                            sig = inspect.signature(obj)
                            param_info = []
                            
                            # 获取函数参数信息
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
                                    param_type_str = (
                                        f"{origin_name}[{args_str}]"
                                    )
                                
                                # 判断参数是否必填
                                required = param.default == inspect.Parameter.empty
                                
                                param_info.append({
                                    "name": param_name,
                                    "type": (
                                        param_type_str 
                                        if param_type_str != '_empty' else 'Any'
                                    ),
                                    "required": required,
                                    "default": (
                                        repr(param.default) if not required else None
                                    )
                                })
                            
                            # 构建工具信息
                            tool_info = {
                                "id": None,  # 动态生成的工具没有ID
                                "name": name,
                                "description": inspect.getdoc(obj) or "",
                                "function_name": name,
                                "parameters": param_info,
                                "return_type": (
                                    str(sig.return_annotation)
                                    if str(sig.return_annotation) != '_empty' 
                                    else 'Any'
                                ),
                                "module_id": module_id,
                                "is_enabled": True
                            }
                            tools.append(tool_info)
                finally:
                    # # 清理临时文件
                    # if os.path.exists(temp_path):
                    #     os.unlink(temp_path)
                    
                    # 从sys.modules中移除临时模块
                    if module_name in sys.modules:
                        del sys.modules[module_name]
            
            except Exception as e:
                import traceback
                from app.utils.logging import mcp_logger
                mcp_logger.error(f"解析模块代码时出错: {str(e)}")
                mcp_logger.error(traceback.format_exc())
                return []
            
            return tools
    
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
                    mcp_logger.warning("数据库中没有找到MCP模块")
                    return stats
                
                mcp_logger.info(f"在数据库中找到{len(modules)}个MCP模块")
                
                # 创建临时目录存放模块代码
                temp_dir = tempfile.mkdtemp(prefix="mcp_modules_")
                
                # 添加临时目录到Python路径
                if temp_dir not in sys.path:
                    sys.path.insert(0, temp_dir)
                
                # 处理每个模块
                for module in modules:
                    if not module.code:
                        mcp_logger.warning(f"模块 {module.name} 没有代码内容，跳过")
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
                        mcp_logger.error(
                            f"处理模块 {module.name} 失败: {str(e)}"
                        )
                
                # 清理临时目录
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    mcp_logger.warning(f"清理临时目录失败: {str(e)}")
                
                db.commit()
                return stats
                
        except Exception as e:
            mcp_logger.error(f"扫描模块时出错: {str(e)}")
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
    
    # 以下函数已移动到 group_service 中
    def list_categories(self) -> List[Dict[str, Any]]:
        """获取所有MCP分组（已移动到 group_service，保留兼容）"""
        from app.services.group.service import group_service
        return group_service.list_categories()
    
    def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        """获取指定MCP分组详情（已移动到 group_service，保留兼容）"""
        from app.services.group.service import group_service
        return group_service.get_category(category_id)
    
    def create_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建MCP分组（已移动到 group_service，保留兼容）"""
        from app.services.group.service import group_service
        return group_service.create_category(data)
    
    def update_category(
        self, category_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新MCP分组（已移动到 group_service，保留兼容）"""
        from app.services.group.service import group_service
        return group_service.update_category(category_id, data)
    
    def delete_category(self, category_id: int) -> bool:
        """删除MCP分组（已移动到 group_service，保留兼容）"""
        from app.services.group.service import group_service
        return group_service.delete_category(category_id)
    
    def update_module_category(
        self, module_id: int, category_id: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """更新模块所属分组（已移动到 group_service，保留兼容）"""
        from app.services.group.service import group_service
        return group_service.update_module_category(module_id, category_id)

    def create_module(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建MCP模块"""
        with get_db() as db:
            # 处理config_schema字段，如果是字典则转换为JSON字符串
            config_schema = data.get("config_schema")
            if config_schema is not None and isinstance(config_schema, dict):
                config_schema = json.dumps(config_schema, ensure_ascii=False)
            elif config_schema is not None and not isinstance(config_schema, str):
                # 如果不是字典也不是字符串，转换为字符串
                config_schema = str(config_schema)
            
            # 构建模块对象
            module = McpModule(
                name=data.get("name", ""),
                description=data.get("description", ""),
                module_path=data.get("module_path", ""),
                author=data.get("author", ""),
                version=data.get("version", "1.0.0"),
                tags=data.get("tags", ""),
                icon=data.get("icon", ""),
                is_hosted=data.get("is_hosted", False),
                repository_url=data.get("repository_url", ""),
                category_id=data.get("category_id"),
                code=data.get("code", ""),
                config_schema=config_schema,
                markdown_docs=data.get("markdown_docs", ""),
                user_id=data.get("user_id"),
                is_public=data.get("is_public", True)
            )
            
            db.add(module)
            db.commit()
            db.refresh(module)
            
            return module.to_dict()
    
    def update_module(
        self, module_id: int, data: Dict[str, Any], 
        user_id: Optional[int] = None, is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        """更新MCP模块
        
        参数:
            module_id: 模块ID
            data: 更新的数据
            user_id: 当前用户ID
            is_admin: 是否为管理员
            
        返回:
            更新后的模块信息，如果没有权限则返回None
        """
        with get_db() as db:
            # 先获取模块
            module = db.query(McpModule).filter(McpModule.id == module_id).first()
            if not module:
                return None
                
            # 检查权限：非管理员只能更新自己创建的模块
            if not is_admin and user_id is not None and module.user_id != user_id:
                return None
            
            # 处理config_schema字段，如果是字典则转换为JSON字符串
            if "config_schema" in data:
                config_schema = data["config_schema"]
                if config_schema is not None and isinstance(config_schema, dict):
                    data["config_schema"] = json.dumps(config_schema, ensure_ascii=False)
                elif config_schema is not None and not isinstance(config_schema, str):
                    # 如果不是字典也不是字符串，转换为字符串
                    data["config_schema"] = str(config_schema)
            
            # 更新字段
            for key, value in data.items():
                if hasattr(module, key) and key != "id":
                    if key == "is_public" and value in ["True", "true", "False", "false"]:
                        # 处理布尔值
                        setattr(module, key, value.lower() == "true")
                    elif key == "config_schema":
                        # config_schema已经在上面处理过了，直接设置
                        setattr(module, key, value)
                    elif isinstance(value, dict):
                        # 处理其他字典类型数据
                        json_data = json.dumps(value, ensure_ascii=False)
                        setattr(module, key, json_data)
                    else:
                        # 其他数据
                        setattr(module, key, value)
            
            # 更新时间
            module.updated_at = now_beijing()
            
            db.commit()
            db.refresh(module)
            
            return module.to_dict()
    
    def delete_module(
        self, module_id: int, 
        user_id: Optional[int] = None, 
        is_admin: bool = False
    ) -> bool:
        """删除MCP模块
        
        参数:
            module_id: 模块ID
            user_id: 当前用户ID
            is_admin: 是否为管理员
            
        返回:
            是否删除成功
        """
        try:
            with get_db() as db:
                # 先获取模块
                module = db.query(McpModule).filter(McpModule.id == module_id).first()
                if not module:
                    return False
                    
                # 检查权限：非管理员只能删除自己创建的模块
                if not is_admin and user_id is not None and module.user_id != user_id:
                    return False
                
                # 删除相关工具
                db.execute(
                    delete(McpTool).where(McpTool.module_id == module_id)
                )
                
                # 删除模块
                db.execute(
                    delete(McpModule).where(McpModule.id == module_id)
                )
                
                db.commit()
                return True
        except SQLAlchemyError as e:
            mcp_logger.error(f"删除模块错误: {str(e)}")
            return False
            
    def clone_module(
        self, module_id: int, user_id: int, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """复制MCP模块
        
        参数:
            module_id: 要复制的模块ID
            user_id: 当前用户ID（新模块的所有者）
            data: 可选的自定义属性，用于覆盖默认复制的属性
            
        返回:
            复制后的新模块信息，如果原模块不存在则返回None
        """
        try:
            with get_db() as db:
                # 获取源模块
                source_module = db.query(McpModule).filter(McpModule.id == module_id).first()
                if not source_module:
                    return None
                
                # 准备新模块的默认数据
                module_data = {
                    "name": f"{source_module.name} - 副本",
                    "description": source_module.description,
                    "module_path": source_module.module_path,
                    "author": source_module.author,
                    "version": source_module.version,
                    "tags": source_module.tags,
                    "icon": source_module.icon,
                    "is_hosted": source_module.is_hosted,
                    "repository_url": source_module.repository_url,
                    "category_id": source_module.category_id,
                    "code": source_module.code,
                    "config_schema": source_module.config_schema,
                    "markdown_docs": source_module.markdown_docs,
                    "user_id": user_id,  # 设置为当前用户
                    "is_public": False   # 默认设为私有
                }
                
                # 如果提供了自定义数据，覆盖默认值
                if data:
                    for key, value in data.items():
                        if key in module_data and key != "user_id":  # 不允许覆盖user_id
                            module_data[key] = value
                
                # 创建新模块
                new_module = McpModule(**module_data)
                
                db.add(new_module)
                db.commit()
                db.refresh(new_module)
                
                return new_module.to_dict()
        except SQLAlchemyError as e:
            mcp_logger.error(f"复制模块错误: {str(e)}")
            return None


# 创建服务实例
marketplace_service = MarketplaceService() 