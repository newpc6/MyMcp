"""
兼容旧路径的 Seed 转发模块。

新增代码请从 app.services.seed_service 导入 ensure_seed_data 或具体 seed 函数。
"""
from app.services.seed_service.base import (
    auto_categorize_modules,
    init_admin_users,
    init_category_data,
    init_demo_modules,
    migrate_database,
)

__all__ = [
    "migrate_database",
    "init_category_data",
    "auto_categorize_modules",
    "init_demo_modules",
    "init_admin_users",
]
