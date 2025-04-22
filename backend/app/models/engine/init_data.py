"""
初始化数据模块

用于在数据库初始化时添加基础数据
"""
from sqlalchemy import select, text
from datetime import datetime
from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpCategory, McpModule
from app.utils.logging import em_logger
from pytz import timezone


def migrate_database():
    """
    迁移数据库结构
    处理表结构变更，例如添加字段等
    """
    try:
        with get_db() as db:
            # 检查mcp_categories表是否存在
            check_categories_sql = text(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='mcp_categories'"
            )
            result = db.execute(check_categories_sql).fetchone()
            if not result:
                # 创建分类表
                em_logger.info("创建mcp_categories表")
                db.execute(text("""
                    CREATE TABLE mcp_categories (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        icon VARCHAR(200),
                        order INTEGER DEFAULT 0,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                """))
                
            # 检查mcp_modules表中是否存在category_id字段
            check_column_sql = text(
                "PRAGMA table_info(mcp_modules)"
            )
            columns = db.execute(check_column_sql).fetchall()
            column_names = [col[1] for col in columns]  # 字段名在结果的第2列
            
            if 'category_id' not in column_names:
                # 添加category_id字段
                em_logger.info("向mcp_modules表添加category_id字段")
                db.execute(text(
                    "ALTER TABLE mcp_modules "
                    "ADD COLUMN category_id INTEGER"
                ))
            
            db.commit()
            em_logger.info("数据库迁移完成")
    except Exception as e:
        em_logger.error(f"数据库迁移失败: {str(e)}")


def init_category_data():
    """
    初始化MCP分类数据
    """
    categories = [
        {"name": "浏览器自动化", "icon": "Monitor", "order": 10},
        {"name": "搜索工具", "icon": "Search", "order": 20},
        {"name": "交流协作工具", "icon": "ChatDotRound", "order": 30},
        {"name": "开发者工具", "icon": "Tools", "order": 40},
        {"name": "娱乐与多媒体", "icon": "Film", "order": 50},
        {"name": "文件系统", "icon": "Folder", "order": 60},
        {"name": "金融", "icon": "Money", "order": 70},
        {"name": "知识管理与记忆", "icon": "Reading", "order": 80},
        {"name": "位置服务", "icon": "Location", "order": 90},
        {"name": "文化与艺术", "icon": "PictureFilled", "order": 100},
        {"name": "学术研究", "icon": "DocumentCopy", "order": 110},
        {"name": "日程管理", "icon": "Calendar", "order": 120},
    ]
    
    with get_db() as db:
        try:
            # 检查是否已有分类数据
            existing = db.execute(select(McpCategory)).scalars().all()
            if existing:
                em_logger.info(f"已存在 {len(existing)} 个MCP分类，跳过初始化")
                return
            
            # 添加分类数据
            now = datetime.now(timezone('Asia/Shanghai'))  # 使用原生datetime对象
            for category_data in categories:
                category = McpCategory(
                    name=category_data["name"],
                    icon=category_data["icon"],
                    order=category_data["order"],
                    created_at=now,
                    updated_at=now
                )
                db.add(category)
            
            db.commit()
            em_logger.info(f"成功初始化 {len(categories)} 个MCP分类")
        except Exception as e:
            db.rollback()
            em_logger.error(f"初始化MCP分类失败: {str(e)}")


def auto_categorize_modules():
    """
    自动对现有模块进行分类
    根据模块名称和描述自动匹配合适的分类
    """
    try:
        with get_db() as db:
            # 获取所有未分类的模块
            uncategorized_modules = db.execute(
                select(McpModule).where(McpModule.category_id.is_(None))
            ).scalars().all()
            
            if not uncategorized_modules:
                em_logger.info("没有需要分类的模块")
                return
            
            # 获取所有分类
            categories = db.execute(select(McpCategory)).scalars().all()
            if not categories:
                em_logger.info("没有可用的分类")
                return
            
            # 分类关键词映射
            category_keywords = {
                "浏览器自动化": ["浏览器", "browser", "自动化", "网页"],
                "搜索工具": ["搜索", "search", "查询", "query", "find", "tavily"],
                "交流协作工具": ["交流", "协作", "chat", "社交"],
                "开发者工具": ["开发", "developer", "编程", "代码", "github"],
                "娱乐与多媒体": ["娱乐", "多媒体", "视频", "音乐", "图片"],
                "文件系统": ["文件", "file", "存储", "目录", "folder"],
                "金融": ["金融", "finance", "支付", "金钱", "财务"],
                "知识管理与记忆": ["知识", "管理", "记忆", "笔记"],
                "位置服务": ["位置", "地图", "location", "地理", "geo"],
                "文化与艺术": ["文化", "艺术", "design", "设计"],
                "学术研究": ["学术", "研究", "academic", "论文"],
                "日程管理": ["日程", "schedule", "日历", "任务"],
            }
            
            # 创建分类ID映射
            category_id_map = {cat.name: cat.id for cat in categories}
            
            # 自动分类计数
            categorized_count = 0
            
            now = datetime.now()  # 使用原生datetime对象
            for module in uncategorized_modules:
                module_text = (
                    (module.name or "") + " " + 
                    (module.description or "") + " " + 
                    (module.module_path or "")
                ).lower()
                
                matched_category = None
                max_matches = 0
                
                # 查找最匹配的分类
                for cat_name, keywords in category_keywords.items():
                    matches = sum(
                        1 for keyword in keywords 
                        if keyword.lower() in module_text
                    )
                    if matches > max_matches:
                        max_matches = matches
                        matched_category = cat_name
                
                # 如果找到匹配的分类，更新模块
                if matched_category and max_matches > 0:
                    category_id = category_id_map.get(matched_category)
                    if category_id:
                        module.category_id = category_id
                        module.updated_at = now
                        categorized_count += 1
            
            if categorized_count > 0:
                db.commit()
                em_logger.info(f"成功自动分类 {categorized_count} 个模块")
            else:
                em_logger.info("没有找到可匹配的模块")
    except Exception as e:
        em_logger.error(f"自动分类模块失败: {str(e)}")
        try:
            db.rollback()
        except Exception:  # 不使用裸except
            pass 