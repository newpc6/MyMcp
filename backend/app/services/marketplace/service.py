"""
MCP广场服务
"""
from typing import List, Dict, Any, Optional

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
        """获取指定的MCP工具信息"""
        with get_db() as db:
            query = select(McpTool).where(McpTool.id == tool_id)
            tool = db.execute(query).scalar_one_or_none()
            if tool:
                return tool.to_dict()
            return None
    
    def scan_repository_modules(self) -> Dict[str, int]:
        """扫描仓库中的MCP模块并更新数据库"""
        # 实现细节省略
        pass
    
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


# 创建服务实例
marketplace_service = MarketplaceService() 