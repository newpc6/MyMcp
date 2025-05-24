"""
权限相关工具函数
"""


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


def add_edit_permission(items, user_id, is_admin=False):
    """
    为查询结果列表中的每个项添加编辑权限标志
    
    Args:
        items: 列表或单个字典对象
        user_id: 当前用户ID
        is_admin: 当前用户是否为管理员
        
    Returns:
        添加了can_edit字段的列表或单个字典对象
    """
    if items is None:
        return items
    
    # 处理单个项
    if isinstance(items, dict):
        item_owner_id = items.get("user_id")
        items["can_edit"] = can_edit(user_id, item_owner_id, is_admin)
        return items
    
    # 处理列表
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                item_owner_id = item.get("user_id")
                item["can_edit"] = can_edit(user_id, item_owner_id, is_admin)
    
    return items


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