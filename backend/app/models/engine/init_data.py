"""
初始化数据模块

用于在数据库初始化时添加基础数据
"""
from sqlalchemy import select
from datetime import datetime
from app.models.engine import get_db
from app.models.modules.mcp_marketplace import McpCategory, McpModule
from app.utils.logging import em_logger
from pytz import timezone


def migrate_database():
    """执行数据库迁移"""
    try:
        # 导入迁移模块
        try:
            from app.models.engine.migrations import get_all_migrations
        except ImportError as e:
            em_logger.warning(f"迁移模块导入失败，使用内置迁移: {str(e)}")
            # 使用内置迁移作为后备方案
            _run_builtin_migrations()
            return
        
        # 获取所有迁移模块
        migrations = get_all_migrations()
        if not migrations:
            em_logger.warning("未找到迁移模块，使用内置迁移")
            _run_builtin_migrations()
            return
            
        em_logger.info(f"找到 {len(migrations)} 个迁移模块")
        
        # 执行所有迁移
        with get_db() as db:
            for migration in migrations:
                try:
                    migration_name = migration.__name__.split('.')[-1]
                    em_logger.info(f"执行迁移: {migration_name}")
                    migration.run(db)
                except Exception as e:
                    em_logger.error(f"迁移 {migration_name} 执行失败: {str(e)}")
                    raise
                
            em_logger.info("所有迁移执行完成")
    
    except Exception as e:
        em_logger.error(f"数据库迁移失败: {str(e)}")


def _run_builtin_migrations():
    """执行内置的迁移，作为后备方案"""
    from sqlalchemy import text
    
    try:
        with get_db() as db:
            # 1. 检查mcp_categories表是否存在
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
            
            # 2. 检查字段
            check_column_sql = text(
                "PRAGMA table_info(mcp_modules)"
            )
            columns = db.execute(check_column_sql).fetchall()
            column_names = [col[1] for col in columns]  # 字段名在结果的第2列
            
            # 3. 添加category_id字段
            if 'category_id' not in column_names:
                em_logger.info("向mcp_modules表添加category_id字段")
                db.execute(text(
                    "ALTER TABLE mcp_modules "
                    "ADD COLUMN category_id INTEGER"
                ))
            
            # 4. 添加code字段
            if 'code' not in column_names:
                em_logger.info("向mcp_modules表添加code字段")
                db.execute(text(
                    "ALTER TABLE mcp_modules "
                    "ADD COLUMN code TEXT"
                ))
            
            # 5. 添加config_schema字段
            if 'config_schema' not in column_names:
                em_logger.info("向mcp_modules表添加config_schema字段")
                db.execute(text(
                    "ALTER TABLE mcp_modules "
                    "ADD COLUMN config_schema TEXT"
                ))
            
            db.commit()
            em_logger.info("内置迁移完成")
    except Exception as e:
        em_logger.error(f"执行内置迁移失败: {str(e)}")
        raise


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


def init_demo_modules():
    """初始化演示模块数据"""
    try:
        with get_db() as db:
            # 检查是否已有模块
            count_query = select(McpModule)
            modules_count = len(db.execute(count_query).all())
            
            # 如果没有模块，添加演示模块
            if modules_count == 0:
                # 获取分类ID
                cat_query = select(McpCategory).where(
                    McpCategory.name == "开发者工具"
                )
                dev_cat = db.execute(cat_query).scalar_one_or_none()
                dev_cat_id = dev_cat.id if dev_cat else None
                
                cat_query = select(McpCategory).where(
                    McpCategory.name == "搜索工具"
                )
                search_cat = db.execute(cat_query).scalar_one_or_none()
                search_cat_id = search_cat.id if search_cat else None
                
                # 添加演示模块1：计算工具
                calc_module = McpModule(
                    name="calculator",
                    description="简单计算工具模块",
                    module_path="repository.calculator",
                    author="系统",
                    version="1.0.0",
                    tags="计算,数学,工具",
                    icon="calculator",
                    is_hosted=True,
                    category_id=dev_cat_id,
                    code="""
\"\"\"
计算工具模块，提供基本的数学计算功能
\"\"\"
from typing import List, Union, Dict, Any


def add_numbers(numbers: List[int]) -> int:
    \"\"\"
    计算一组数字的和
    
    参数:
        numbers: 需要求和的数字列表
        
    返回:
        所有数字的和
    \"\"\"
    return sum(numbers)


def multiply_numbers(numbers: List[int]) -> int:
    \"\"\"
    计算一组数字的乘积
    
    参数:
        numbers: 需要相乘的数字列表
        
    返回:
        所有数字的乘积
    \"\"\"
    if not numbers:
        return 0
    
    result = 1
    for num in numbers:
        result *= num
    return result


def calculate_expression(expression: str) -> Dict[str, Any]:
    \"\"\"
    计算数学表达式
    
    参数:
        expression: 数学表达式字符串，如 "1 + 2 * 3"
        
    返回:
        计算结果和解析过程
    \"\"\"
    try:
        # 安全的表达式评估
        result = eval(expression, {"__builtins__": {}})
        
        return {
            "expression": expression,
            "result": result,
            "success": True
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "success": False
        }
""",               
                    markdown_docs="""
# 计算工具模块

## 简介
计算工具模块提供基本的数学计算功能，包括加法、乘法和复杂表达式计算。

## 功能列表
本模块提供以下工具函数：

### 1. 数字求和
将一组数字相加，返回它们的总和。

### 2. 数字乘积
计算一组数字的乘积，返回它们相乘的结果。

### 3. 表达式计算
支持计算复杂的数学表达式，如`1 + 2 * 3`等。

## 使用示例
```python
# 计算数字之和
result = add_numbers([1, 2, 3, 4, 5])  # 返回 15

# 计算数字乘积
product = multiply_numbers([2, 3, 4])  # 返回 24

# 计算表达式
expr_result = calculate_expression("2 + 3 * 4")  
# 返回 {'expression': '2 + 3 * 4', 'result': 14, 'success': True}
```

## 注意事项
表达式计算功能出于安全考虑使用了受限的环境，不支持导入模块和执行系统命令。
"""
                )
                db.add(calc_module)
                
                # 添加演示模块2：Web搜索工具
                search_module = McpModule(
                    name="web_search",
                    description="网络搜索工具模块",
                    module_path="repository.web_search",
                    author="系统",
                    version="1.0.0",
                    tags="搜索,网络,工具",
                    icon="search",
                    is_hosted=True,
                    category_id=search_cat_id,
                    config_schema="""
{
    "api_key": {
        "type": "string",
        "description": "搜索API密钥",
        "required": true
    },
    "search_engine": {
        "type": "string",
        "description": "搜索引擎类型",
        "choices": ["google", "bing", "baidu"],
        "default": "google"
    },
    "result_count": {
        "type": "integer",
        "description": "返回结果数量",
        "default": 5,
        "min": 1,
        "max": 20
    }
}
""",
                    code="""
\"\"\"
网络搜索工具模块，提供基本的网络搜索功能
\"\"\"
from typing import List, Dict, Any, Optional

# 配置模式，定义需要的配置字段
CONFIG_SCHEMA = {
    "api_key": {
        "type": "string",
        "description": "搜索API密钥",
        "required": True
    },
    "search_engine": {
        "type": "string",
        "description": "搜索引擎类型",
        "choices": ["google", "bing", "baidu"],
        "default": "google"
    },
    "result_count": {
        "type": "integer",
        "description": "返回结果数量",
        "default": 5,
        "min": 1,
        "max": 20
    }
}

# 演示用配置，实际会被用户配置覆盖
config = {
    "api_key": "demo_key",
    "search_engine": "google",
    "result_count": 5
}


def search_web(
    query: str, result_count: Optional[int] = None
) -> Dict[str, Any]:
    \"\"\"
    在网络上搜索内容
    
    参数:
        query: 搜索查询词
        result_count: 返回结果数量，如果不指定则使用配置值
        
    返回:
        搜索结果和元数据
    \"\"\"
    # 使用配置中的值或参数中的值
    count = result_count or config.get("result_count", 5)
    
    # 演示用结果
    demo_results = [
        {
            "title": f"搜索结果 1 - {query}",
            "url": f"https://example.com/1?q={query}",
            "snippet": f"这是关于 {query} 的第一个结果的摘要内容..."
        },
        {
            "title": f"搜索结果 2 - {query}",
            "url": f"https://example.com/2?q={query}",
            "snippet": f"这是关于 {query} 的另一个相关页面..."
        },
        {
            "title": f"详解{query}的完整指南",
            "url": f"https://example.com/guide?topic={query}",
            "snippet": f"{query}的完整教程和指南，包含详细的步骤和示例..."
        },
        {
            "title": f"{query} 相关的最新新闻",
            "url": f"https://example.com/news?topic={query}",
            "snippet": f"最新的关于{query}的新闻报道和行业动态..."
        },
        {
            "title": f"{query} 官方文档和资源",
            "url": f"https://example.com/docs?subject={query}",
            "snippet": f"官方提供的{query}文档、API参考和开发资源..."
        }
    ]
    
    # 根据请求数量返回结果
    actual_results = demo_results[:min(count, len(demo_results))]
    
    return {
        "query": query,
        "results": actual_results,
        "total_results": len(actual_results),
        "search_engine": config.get("search_engine", "google"),
        "success": True
    }


def get_trending_topics() -> List[str]:
    \"\"\"
    获取当前热门搜索话题
    
    返回:
        热门话题列表
    \"\"\"
    # 演示用热门话题
    return [
        "人工智能最新进展",
        "Web开发趋势2024",
        "数据科学教程",
        "Python编程技巧",
        "云计算服务比较"
    ]
""",
                    markdown_docs="""
# Web搜索工具

## 简介
Web搜索工具模块提供网络搜索功能，可以从互联网上获取信息和热门话题。

## 配置项
该模块需要以下配置：

| 配置项 | 类型 | 描述 | 默认值 |
|-------|-----|------|-------|
| api_key | 字符串 | 搜索API密钥 | 必填 |
| search_engine | 字符串 | 搜索引擎类型 | google |
| result_count | 整数 | 返回结果数量 | 5 |

## 功能列表

### 1. 网络搜索
根据查询词在网络上搜索内容，返回相关结果。

**参数：**
- query: 搜索查询词
- result_count: 返回结果数量（可选）

**返回：**
- 包含搜索结果的对象，包括查询词、结果列表、总结果数等

### 2. 获取热门话题
获取当前互联网上的热门搜索话题。

**返回：**
- 热门话题字符串列表

## 使用示例
```python
# 搜索网络内容
results = search_web("人工智能", 3)
# 返回前3条关于"人工智能"的搜索结果

# 获取热门话题
topics = get_trending_topics()
# 返回当前热门话题列表
```

## 注意事项
1. 在实际使用前，需要设置有效的API密钥
2. 搜索结果数量限制为1-20之间
3. 支持的搜索引擎包括Google、Bing和百度
"""
                )
                db.add(search_module)
                
                db.commit()
                em_logger.info("初始化了演示模块数据")
    
    except Exception as e:
        em_logger.error(f"初始化演示模块失败: {str(e)}") 