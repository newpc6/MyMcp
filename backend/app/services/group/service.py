"""
分组服务实现
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError

from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpModule
from app.models.group.group import McpGroup
from app.core.utils import now_beijing
from app.utils.logging import em_logger
from app.utils.permissions import add_edit_permission


class GroupService:
    """分组服务"""
    
    def list_group(self, user_id: Optional[int] = None, 
                   is_admin: bool = False) -> List[Dict[str, Any]]:
        """获取所有MCP分组"""
        with get_db() as db:
            query = select(McpGroup).order_by(McpGroup.order)
            categories = db.execute(query).scalars().all()
            result = [c.to_dict() for c in categories]
            # 添加可编辑字段
            return add_edit_permission(result, user_id, is_admin)
    
    def get_category(self, category_id: int, user_id: Optional[int] = None, 
                     is_admin: bool = False) -> Optional[Dict[str, Any]]:
        """获取指定MCP分组详情"""
        with get_db() as db:
            query = select(McpGroup).where(McpGroup.id == category_id)
            category = db.execute(query).scalar_one_or_none()
            if category:
                result = category.to_dict()
                # 添加可编辑字段
                return add_edit_permission(result, user_id, is_admin)
            return None
    
    def create_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建MCP分组"""
        with get_db() as db:
            # 获取最大排序号
            max_order_query = select(McpGroup).order_by(
                McpGroup.order.desc()
            )
            max_order_category = db.execute(
                max_order_query
            ).first()
            if max_order_category:
                max_order = max_order_category[0].order + 10
            else:
                max_order = 0
            
            # 创建新分组
            category = McpGroup(
                name=data["name"],
                description=data.get("description"),
                icon=data.get("icon"),
                order=data.get("order", max_order),
                created_at=now_beijing(),
                updated_at=now_beijing(),
                user_id=data.get("user_id")  # 保存创建者ID
            )
            
            db.add(category)
            db.commit()
            db.refresh(category)
            
            return category.to_dict()
    
    def update_category(
        self, category_id: int, data: Dict[str, Any],
        user_id: Optional[int] = None, is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        """更新MCP分组"""
        with get_db() as db:
            # 检查分组是否存在
            category_query = select(McpGroup).where(
                McpGroup.id == category_id
            )
            category = db.execute(category_query).scalar_one_or_none()
            if not category:
                return None
            
            # 检查权限：非管理员只能更新自己创建的分组
            if not is_admin and user_id is not None:
                if category.user_id != user_id:
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
                update(McpGroup)
                .where(McpGroup.id == category_id)
                .values(**update_data)
            )
            db.execute(stmt)
            db.commit()
            
            # 返回更新后的分组信息
            updated_category = db.execute(category_query).scalar_one()
            result = updated_category.to_dict()
            # 添加可编辑字段
            return add_edit_permission(result, user_id, is_admin)
    
    def delete_category(self, category_id: int, user_id: Optional[int] = None, 
                        is_admin: bool = False) -> bool:
        """删除MCP分组"""
        with get_db() as db:
            try:
                # 检查分组是否存在
                category_query = select(McpGroup).where(
                    McpGroup.id == category_id
                )
                category = db.execute(category_query).scalar_one_or_none()
                if not category:
                    return False
                
                # 检查权限：非管理员只能删除自己创建的分组
                if not is_admin and user_id is not None:
                    if category.user_id != user_id:
                        return False
                
                # 先将该分组下的模块解除关联
                stmt = (
                    update(McpModule)
                    .where(McpModule.category_id == category_id)
                    .values(category_id=None)
                )
                db.execute(stmt)
                
                # 删除分组
                stmt = delete(McpGroup).where(McpGroup.id == category_id)
                db.execute(stmt)
                db.commit()
                return True
            except SQLAlchemyError as e:
                em_logger.error(f"删除分组失败: {str(e)}")
                db.rollback()
                return False
    
    def update_module_category(
        self, module_id: int, category_id: Optional[int],
        user_id: Optional[int] = None, is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        """更新模块所属分组"""
        with get_db() as db:
            # 检查模块是否存在
            module_query = select(McpModule).where(McpModule.id == module_id)
            module = db.execute(module_query).scalar_one_or_none()
            if not module:
                return None
            
            # 检查权限：非管理员只能更新自己创建的模块
            if not is_admin and user_id is not None:
                if module.user_id != user_id:
                    return None
                
            # 如果提供了分组ID，检查分组是否存在
            if category_id is not None:
                category_query = select(McpGroup).where(
                    McpGroup.id == category_id
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
            result = updated_module.to_dict()
            # 添加可编辑字段
            return add_edit_permission(result, user_id, is_admin)


# 创建服务实例
group_service = GroupService() 