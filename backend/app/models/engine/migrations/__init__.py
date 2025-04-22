"""
数据库迁移模块

按顺序导入所有迁移
"""
import os
import importlib
import re
from app.utils.logging import em_logger

# 迁移文件正则表达式：匹配V{数字}_{描述}.py格式
MIGRATION_PATTERN = re.compile(r'^V(\d+)_.*\.py$')


def get_migration_files():
    """获取按序号排列的迁移文件列表"""
    # 当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    migrations = []
    
    # 确保目录存在
    if not os.path.exists(current_dir):
        em_logger.warning(f"迁移目录不存在: {current_dir}")
        return migrations
    
    # 遍历当前目录中的文件
    for filename in os.listdir(current_dir):
        match = MIGRATION_PATTERN.match(filename)
        if match:
            version = int(match.group(1))
            module_name = filename[:-3]  # 去掉.py后缀
            migrations.append((version, module_name))
    
    # 按版本号排序
    migrations.sort(key=lambda x: x[0])
    return migrations


def get_all_migrations():
    """获取所有迁移模块"""
    migrations = []
    migration_files = get_migration_files()
    
    # 导入每个迁移模块
    for _, module_name in migration_files:
        try:
            package = "app.models.engine.migrations"
            module = importlib.import_module(f"{package}.{module_name}")
            migrations.append(module)
        except ImportError as e:
            em_logger.error(f"导入迁移模块 {module_name} 失败: {str(e)}")
    
    return migrations 