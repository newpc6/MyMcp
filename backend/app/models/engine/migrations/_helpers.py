"""数据库迁移辅助函数。"""
from sqlalchemy import inspect, text


def table_exists(db, table_name: str) -> bool:
    """检查表是否存在，兼容 SQLite / MySQL。"""
    inspector = inspect(db.get_bind())
    return table_name in inspector.get_table_names()


def get_column(db, table_name: str, column_name: str):
    """获取列元数据，不存在时返回 None。"""
    inspector = inspect(db.get_bind())
    for column in inspector.get_columns(table_name):
        if column["name"] == column_name:
            return column
    return None


def quote_identifier(db, identifier: str) -> str:
    """按当前数据库方言引用标识符。"""
    return db.get_bind().dialect.identifier_preparer.quote(identifier)


def rename_table_if_needed(db, old_name: str, new_name: str) -> bool:
    """旧表存在且新表不存在时重命名表。"""
    old_exists = table_exists(db, old_name)
    new_exists = table_exists(db, new_name)

    if new_exists:
        return False
    if not old_exists:
        return False

    old_table = quote_identifier(db, old_name)
    new_table = quote_identifier(db, new_name)
    db.execute(text(f"ALTER TABLE {old_table} RENAME TO {new_table}"))
    return True
