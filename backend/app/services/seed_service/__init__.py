"""
Seed 初始化服务入口。

外部模块只调用 ensure_seed_data，具体 seed 过程按职责拆到独立文件。
"""
from .base import (
    auto_categorize_modules,
    init_admin_users,
    init_category_data,
    init_demo_modules,
    migrate_database,
)


def ensure_seed_data(run_migrations: bool = True) -> None:
    """按依赖顺序初始化数据库基础数据。"""
    if run_migrations:
        migrate_database()
    init_category_data()
    auto_categorize_modules()
    init_demo_modules()
    init_admin_users()


__all__ = [
    "ensure_seed_data",
    "migrate_database",
    "init_category_data",
    "auto_categorize_modules",
    "init_demo_modules",
    "init_admin_users",
]
