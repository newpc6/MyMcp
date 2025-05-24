"""
权限相关工具函数
"""
from typing import Dict, List, Optional, Union, Set
from app.utils.logging import em_logger


def can_edit(user_id, item_owner_id, is_admin=False):
    """
    判断当前用户是否有编辑权限
    规则：只有创建者或管理员才能编辑

    Args:
        user_id: 当前用户ID
        item_owner_id: 项目创建者ID
        is_admin: 当前用户是否为管理员

    Returns:
        bool: 是否有编辑权限
    """
    if is_admin:
        return True
    
    if user_id is None:
        return False
    
    return user_id == item_owner_id


def add_edit_permission(
    items: Union[Dict, List], 
    user_id: Optional[int] = None, 
    is_admin: bool = False
) -> Union[Dict, List]:
    """
    为查询结果列表中的每个项添加编辑权限标志和创建者用户名
    
    Args:
        items: 列表或单个字典对象
        user_id: 当前用户ID
        is_admin: 当前用户是否为管理员
        
    Returns:
        添加了can_edit字段和username字段的列表或单个字典对象
    """
    if items is None:
        return items
    
    # 单个项的处理逻辑
    if isinstance(items, dict):
        # 添加编辑权限
        item_owner_id = items.get("user_id")
        items["can_edit"] = can_edit(user_id, item_owner_id, is_admin)
        
        # 处理用户名
        if "username" not in items and item_owner_id is not None:
            # 为单个项查询用户名
            username_map = _get_usernames_by_ids([item_owner_id])
            username = username_map.get(item_owner_id, f"用户{item_owner_id}")
            items["username"] = username
        return items
    
    # 处理列表
    if isinstance(items, list):
        # 收集所有需要查询的用户ID
        user_ids = set()
        for item in items:
            if isinstance(item, dict) and "username" not in item:
                item_owner_id = item.get("user_id")
                if item_owner_id is not None:
                    user_ids.add(item_owner_id)
        
        # 一次性查询所有用户名
        username_map = _get_usernames_by_ids(user_ids)
        
        # 为每个项添加编辑权限和用户名
        for item in items:
            if isinstance(item, dict):
                # 添加编辑权限
                item_owner_id = item.get("user_id")
                item["can_edit"] = can_edit(user_id, item_owner_id, is_admin)
                
                # 添加用户名（如果尚未存在）
                if "username" not in item and item_owner_id is not None:
                    username = username_map.get(
                        item_owner_id, f"用户{item_owner_id}"
                    )
                    item["username"] = username
    
    return items


def _get_usernames_by_ids(user_ids: Set[int]) -> Dict[int, str]:
    """
    根据用户ID集合批量获取用户名
    
    Args:
        user_ids: 用户ID集合
        
    Returns:
        Dict[int, str]: 用户ID到用户名的映射字典
    """
    if not user_ids:
        return {}
        
    try:
        from app.models.engine import get_db
        from app.models.modules.users import User
        
        username_map = {}
        with get_db() as db:
            users = db.query(User).filter(User.id.in_(user_ids)).all()
            for user in users:
                username_map[user.id] = user.username
        return username_map
    except Exception as e:
        # 如果发生错误，例如数据库连接问题或模型导入问题，返回空字典
        em_logger.error(f"获取用户名失败: {e}")
        return {}


def get_user_info(request):
    """
    从请求中获取用户信息
    
    Args:
        request: Starlette请求对象
    
    Returns:
        tuple: (user_id, is_admin) 用户ID和是否为管理员
    """
    user = request.state.user if hasattr(request, 'state') else None
    user_id = user.get("user_id") if user else None
    is_admin = user.get("is_admin", False) if user else False
    
    return user_id, is_admin 