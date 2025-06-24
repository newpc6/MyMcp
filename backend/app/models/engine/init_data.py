"""
初始化数据模块

用于在数据库初始化时添加基础数据
"""
from sqlalchemy import select
from datetime import datetime
from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpModule
from app.models.group.group import McpGroup
from app.utils.logging import mcp_logger
from pytz import timezone
from app.models.modules.users import Tenant, User
from app.services.users import UserService, TenantService


def migrate_database():
    """执行数据库迁移"""
    try:
        # 导入迁移模块
        try:
            from app.models.engine.migrations import get_all_migrations
        except ImportError as e:
            mcp_logger.warning(f"迁移模块导入失败，使用内置迁移: {str(e)}")
            return

        # 获取所有迁移模块
        migrations = get_all_migrations()
        if not migrations:
            mcp_logger.warning("未找到迁移模块，使用内置迁移")
            return

        mcp_logger.info(f"找到 {len(migrations)} 个迁移模块")

        # 执行所有迁移
        with get_db() as db:
            for migration in migrations:
                try:
                    migration_name = migration.__name__.split('.')[-1]
                    mcp_logger.info(f"执行迁移: {migration_name}")
                    migration.run(db)
                except Exception as e:
                    mcp_logger.error(f"迁移 {migration_name} 执行失败: {str(e)}")
                    raise

            mcp_logger.info("所有迁移执行完成")

    except Exception as e:
        mcp_logger.error(f"数据库迁移失败: {str(e)}")


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
        {"name": "数据库工具", "icon": "DataBase", "order": 130},
        {"name": "网络工具", "icon": "Globe", "order": 140},
        {"name": "数据处理工具", "icon": "DataAnalysis", "order": 150},
    ]

    with get_db() as db:
        try:
            # 检查是否已有分类数据
            existing = db.execute(select(McpGroup)).scalars().all()
            if existing:
                mcp_logger.info(f"已存在 {len(existing)} 个MCP分类，跳过初始化")
                return

            # 添加分类数据
            now = datetime.now(timezone('Asia/Shanghai'))  # 使用原生datetime对象
            for category_data in categories:
                category = McpGroup(
                    name=category_data["name"],
                    icon=category_data["icon"],
                    order=category_data["order"],
                    created_at=now,
                    updated_at=now
                )
                db.add(category)

            db.commit()
            mcp_logger.info(f"成功初始化 {len(categories)} 个MCP分类")
        except Exception as e:
            db.rollback()
            mcp_logger.error(f"初始化MCP分类失败: {str(e)}")


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
                mcp_logger.info("没有需要分类的模块")
                return

            # 获取所有分类
            categories = db.execute(select(McpGroup)).scalars().all()
            if not categories:
                mcp_logger.info("没有可用的分类")
                return

            # 分类关键词映射
            category_keywords = {
                "浏览器自动化": ["浏览器", "browser", "自动化", "网页"],
                "搜索工具": ["搜索", "search", "查询", "query", "find", "tavily"],
                "交流协作工具": ["交流", "协作", "chat", "社交"],
                "开发者工具": ["开发", "developer", "编程", "代码", "github",
                              "计算", "calculator", "文件", "file", "文本",
                              "text"],
                "娱乐与多媒体": ["娱乐", "多媒体", "视频", "音乐", "图片"],
                "文件系统": ["文件", "file", "存储", "目录", "folder"],
                "金融": ["金融", "finance", "支付", "金钱", "财务"],
                "知识管理与记忆": ["知识", "管理", "记忆", "笔记"],
                "位置服务": ["位置", "地图", "location", "地理", "geo"],
                "文化与艺术": ["文化", "艺术", "design", "设计"],
                "学术研究": ["学术", "研究", "academic", "论文"],
                "日程管理": ["日程", "schedule", "日历", "任务"],
                "数据库工具": ["数据库", "database", "mysql", "sql", "查询",
                              "db_utils"],
                "网络工具": ["网络", "http", "api", "请求", "client", "url",
                            "下载"],
                "数据处理工具": ["数据", "json", "处理", "格式化", "验证", "分析"],
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
                mcp_logger.info(f"成功自动分类 {categorized_count} 个模块")
            else:
                mcp_logger.info("没有找到可匹配的模块")
    except Exception as e:
        mcp_logger.error(f"自动分类模块失败: {str(e)}")
        try:
            db.rollback()
        except Exception:  # 不使用裸except
            pass


def init_demo_modules():
    """初始化演示模块数据"""
    import json
    from pathlib import Path
    
    try:
        with get_db() as db:
            # 模板文件夹路径
            template_dir = Path(__file__).parent / "mcp-template"
            
            if not template_dir.exists():
                mcp_logger.warning(f"模板目录不存在: {template_dir}")
                return
            
            # 获取所有分类，建立名称到ID的映射
            categories = db.execute(select(McpGroup)).scalars().all()
            category_map = {cat.name: cat.id for cat in categories}
            
            # 需要检查的模板名称列表
            template_names = [
                "http_client",
                "数据库助手", 
                "file_manager",
                "text_processor"
            ]
            
            # 检查数据库中是否已存在这些模块
            existing_modules = db.execute(
                select(McpModule).where(McpModule.name.in_(template_names))
            ).scalars().all()
            existing_names = {module.name for module in existing_modules}
            
            # 遍历模板文件
            imported_count = 0
            for template_file in template_dir.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                    
                    # 检查模块名称是否在需要检查的列表中
                    module_name = template_data["name"]
                    if module_name not in template_names:
                        continue
                        
                    # 如果模块已存在，跳过
                    if module_name in existing_names:
                        mcp_logger.info(f"模块 {module_name} 已存在，跳过导入")
                        continue
                    
                    # 获取分类ID
                    category_name = template_data.get("category", "开发者工具")
                    category_id = category_map.get(category_name)
                    
                    if not category_id:
                        # 如果分类不存在，使用默认分类
                        category_id = category_map.get("开发者工具")
                    
                    # 创建模块对象
                    module = McpModule(
                        name=template_data["name"],
                        description=template_data["description"],
                        module_path=template_data["module_path"],
                        author=template_data["author"],
                        version=template_data["version"],
                        tags=template_data["tags"],
                        icon=template_data["icon"],
                        is_hosted=template_data["is_hosted"],
                        category_id=category_id,
                        config_schema=template_data.get("config_schema"),
                        code=template_data["code"],
                        markdown_docs=template_data["markdown_docs"],
                        is_public=True  # 发布为公开服务
                    )
                    
                    db.add(module)
                    mcp_logger.info(f"导入模板模块: {template_data['name']}")
                    imported_count += 1
                    
                except Exception as e:
                    mcp_logger.error(f"加载模板文件 {template_file} 失败: "
                                     f"{str(e)}")
                    continue

            if imported_count > 0:
                db.commit()
                mcp_logger.info(f"成功导入 {imported_count} 个模板模块为公开服务")
            else:
                mcp_logger.info("没有需要导入的新模板模块")

    except Exception as e:
        mcp_logger.error(f"初始化演示模块失败: {str(e)}")


def init_admin_users():
    """初始化管理员用户数据"""
    # 创建初始管理员用户

    try:
        with get_db() as db:
            # 检查是否已有管理员用户
            count_query = select(User).where(User.username == "admin")
            admin_count = len(db.execute(count_query).scalars().all())

            if not admin_count:
                mcp_logger.info("创建默认管理员用户")

                # 检查是否已有默认租户
                default_tenant_query = select(Tenant).where(
                    Tenant.code == "default")
                default_tenant_count = len(
                    db.execute(default_tenant_query).scalars().all())

                if not default_tenant_count:
                    # 创建默认租户
                    default_tenant = TenantService.create_tenant(
                        name="默认租户",
                        description="系统默认租户",
                        code="default"
                    )

                # 修改默认密码为 mcp@12345
                UserService.create_user(
                    username="admin",
                    password="mcp@12345",
                    fullname="系统管理员",
                    is_admin=True,
                    tenant_ids=[default_tenant.id]
                )
    except Exception as e:
        mcp_logger.error(f"初始化管理员用户失败: {str(e)}")
