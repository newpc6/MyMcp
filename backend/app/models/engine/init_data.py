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
    try:
        with get_db() as db:
            # 检查是否已有模块
            count_query = select(McpModule)
            modules_count = len(db.execute(count_query).all())

            # 如果没有模块，添加演示模块
            if modules_count == 0:
                # 获取分类ID
                cat_query = select(McpGroup).where(
                    McpGroup.name == "开发者工具"
                )
                dev_cat = db.execute(cat_query).scalar_one_or_none()
                dev_cat_id = dev_cat.id if dev_cat else None

                cat_query = select(McpGroup).where(
                    McpGroup.name == "搜索工具"
                )
                search_cat = db.execute(cat_query).scalar_one_or_none()
                search_cat_id = search_cat.id if search_cat else None

                cat_query = select(McpGroup).where(
                    McpGroup.name == "数据库工具"
                )
                db_cat = db.execute(cat_query).scalar_one_or_none()
                db_cat_id = db_cat.id if db_cat else search_cat_id

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

                # 添加演示模块3：Tavily搜索助手
                tavily_module = McpModule(
                    name="tavily_search",
                    description="使用Tavily API进行实时在线搜索",
                    module_path="repository.tavily_search",
                    author="系统",
                    version="1.0.0",
                    tags="搜索,Tavily,实时搜索,网络搜索",
                    icon="search",
                    is_hosted=True,
                    category_id=search_cat_id,
                    config_schema="""
{
    "api_key": {
        "type": "string",
        "description": "Tavily API密钥",
        "required": true
    }
}
""",
                    code="""
\"\"\"
Tavily搜索助手，提供实时在线搜索功能
\"\"\"
from tavily import TavilyClient
import json

def online_search(query):
    \"\"\"
    使用tavily sdk在线实时搜索

    工具参数:
    query (str): 要搜索的查询字符串。
    
    平台配置参数：
    ${api_key}: 平台API密钥, 请在平台配置，平台运行时会自动替换。

    返回:
    包含搜索结果的字典列表。如果没有结果，则返回 None。
    \"\"\"
    tavily_client = TavilyClient(${api_key})
    response = tavily_client.search(query)
    
    if response.get("results"):
        # 将Unicode转义序列解析为中文并转换为英文
        results = []
        for item in response.get("results"):
            # 如果结果已经是字典格式直接使用
            if isinstance(item, dict):
                results.append(item)
            # 如果结果是JSON字符串需要解析
            else:
                try:
                    item_dict = json.loads(item)
                    results.append(item_dict)
                except json.JSONDecodeError:
                    results.append({"content": item})
        
        return json.dumps(results)
    else:
        return None
""",
                    markdown_docs="""
# Tavily搜索助手

## 简介
Tavily搜索助手利用Tavily API提供实时在线搜索功能，可以获取最新的互联网内容。

## 配置项
该模块需要以下配置：

| 配置项 | 类型 | 描述 | 默认值 |
|-------|-----|------|-------|
| api_key | 字符串 | Tavily API密钥 | 必填 |

## 功能列表

### 在线搜索
根据查询词在互联网上实时搜索内容，返回相关结果。

**参数：**
- query: 搜索查询词

**返回：**
- 包含搜索结果的JSON字符串，每个结果包含内容和元数据
- 如果没有结果，则返回None

## 使用示例
```python
# 搜索"人工智能最新进展"
results = online_search("人工智能最新进展")
# 返回相关的搜索结果
```

## 注意事项
1. 使用前需要在平台配置有效的Tavily API密钥
2. 需要安装tavily-python库
3. 结果内容可能包含HTML标记，根据需要进行处理
"""
                )
                db.add(tavily_module)

                # 添加演示模块4：数据库工具助手
                db_utils_module = McpModule(
                    name="数据库助手",
                    description="数据库操作工具模块",
                    module_path="repository.db_utils",
                    author="系统",
                    version="1.0.0",
                    tags="数据库,MySQL,查询,SQL",
                    icon="database",
                    is_hosted=True,
                    category_id=db_cat_id,
                    config_schema="""
{
    "database_host": {
        "type": "string",
        "description": "数据库主机地址",
        "required": true
    },
    "database_port": {
        "type": "integer",
        "description": "数据库端口",
        "default": 3306
    },
    "database_user": {
        "type": "string",
        "description": "数据库用户名",
        "required": true
    },
    "database_password": {
        "type": "string",
        "description": "数据库密码",
        "required": true
    },
    "database_name": {
        "type": "string",
        "description": "数据库名称",
        "required": true
    }
}
""",
                    code="""
\"\"\"
数据库工具助手，提供数据库操作功能
\"\"\"
from decimal import Decimal
import pymysql
import json
from datetime import datetime


def _connect_database():
    \"\"\"
    连接到数据库

    平台配置参数 (使用${参数名}格式):
    host: 数据库主机地址
    port: 数据库端口
    user: 数据库用户名
    password: 数据库密码
    database: 数据库名称

    返回:
    connection: 数据库连接对象
    \"\"\"
    try:
        connection = pymysql.connect(
            host=${database_host},
            port=${database_port},
            user=${database_user},
            password=${database_password},
            database=${database_name},
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        raise Exception(f"数据库连接失败: {str(e)}")


def _type_to_str(type):
    \"\"\"将不同类型转换为字符串格式\"\"\"
    if isinstance(type, datetime):
        return type.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(type, Decimal):
        return str(type)
    else:
        return type


def get_all_tables():
    \"\"\"
    获取数据库中所有表的列表

    返回:
    数据库中所有表名的JSON字符串
    \"\"\"
    try:
        connection = _connect_database()
        with connection.cursor() as cursor:
            # 查询所有表信息
            sql = \"\"\"
            SELECT 
                table_name as name,
                table_comment as comment,
                create_time,
                update_time
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            ORDER BY table_name
            \"\"\"

            cursor.execute(sql)
            results = cursor.fetchall()

            # 处理类型转换
            for item in results:
                for key, value in item.items():
                    item[key] = _type_to_str(value)

            return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        if 'connection' in locals() and connection:
            connection.close()


def get_table_columns(table_name):
    \"\"\"
    获取指定表的所有字段信息
    
    工具参数:
    table_name (str): 表名
    
    返回:
    表字段信息的JSON字符串
    \"\"\"
    try:
        connection = _connect_database()
        with connection.cursor() as cursor:
            # 验证表名
            if not table_name:
                return json.dumps({"error": "表名不能为空"}, ensure_ascii=False)
            
            # 查询表字段信息
            sql = \"\"\"
            SELECT
                column_name as name,
                column_type as type,
                column_comment as comment,
                is_nullable as nullable,
                column_key as 'key',
                column_default as 'default',
                extra
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
            AND table_name = %s
            ORDER BY ordinal_position
            \"\"\"
            
            cursor.execute(sql, (table_name,))
            results = cursor.fetchall()
            
            return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        if 'connection' in locals() and connection:
            connection.close()


def execute_raw_query(sql, limit=100):
    \"\"\"
    执行自定义SQL查询

    工具参数:
    sql (str): SQL查询语句
    limit (int): 返回结果数量限制，默认为100

    返回:
    查询结果的JSON字符串
    \"\"\"
    try:
        connection = _connect_database()
        with connection.cursor() as cursor:
            # 限制查询类型，只允许SELECT查询
            sql_lower = sql.lower().strip()
            if not sql_lower.startswith('select'):
                return json.dumps(
                    {"error": "只允许执行SELECT查询"},
                    ensure_ascii=False
                )

            # 添加限制条件
            if 'limit' not in sql_lower:
                sql = f"{sql} LIMIT {limit}"

            cursor.execute(sql)
            results = cursor.fetchall()

            # 处理类型转换
            for item in results:
                for key, value in item.items():
                    item[key] = _type_to_str(value)

            return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        if 'connection' in locals() and connection:
            connection.close()


def get_table_data(table_name, columns=None, where=None, order_by=None, limit=100):
    \"\"\"
    获取表数据

    工具参数:
    table_name (str): 表名
    columns (str): 要查询的列，多个列用逗号分隔，默认为*
    where (str): WHERE条件语句，不包含WHERE关键字
    order_by (str): ORDER BY语句，不包含ORDER BY关键字
    limit (int): 返回结果数量限制，默认为100

    返回:
    表数据的JSON字符串
    \"\"\"
    try:
        connection = _connect_database()
        with connection.cursor() as cursor:
            # 验证表名
            if not table_name:
                return json.dumps({"error": "表名不能为空"}, ensure_ascii=False)

            # 构建查询语句
            select_cols = "*" if not columns else columns
            sql = f"SELECT {select_cols} FROM `{table_name}`"

            if where:
                sql += f" WHERE {where}"

            if order_by:
                sql += f" ORDER BY {order_by}"

            sql += f" LIMIT {limit}"

            cursor.execute(sql)
            results = cursor.fetchall()

            # 处理类型转换
            for item in results:
                for key, value in item.items():
                    item[key] = _type_to_str(value)

            return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        if 'connection' in locals() and connection:
            connection.close()
""",
                    markdown_docs="""
# 数据库工具助手

## 简介
数据库工具助手提供MySQL数据库操作功能，包括查询表结构、获取表数据和执行自定义SQL查询等功能。

## 配置项
该模块需要以下配置：

| 配置项 | 类型 | 描述 | 默认值 |
|-------|-----|------|-------|
| database_host | 字符串 | 数据库主机地址 | 必填 |
| database_port | 整数 | 数据库端口 | 3306 |
| database_user | 字符串 | 数据库用户名 | 必填 |
| database_password | 字符串 | 数据库密码 | 必填 |
| database_name | 字符串 | 数据库名称 | 必填 |

## 功能列表

### 1. 获取所有表
获取数据库中所有表的列表及其基本信息。

**返回：**
- 包含表名、注释、创建时间和更新时间的JSON字符串

### 2. 获取表字段
获取指定表的所有字段信息。

**参数：**
- table_name: 表名

**返回：**
- 包含字段名、类型、注释等信息的JSON字符串

### 3. 执行自定义SQL查询
执行用户提供的SQL查询语句。

**参数：**
- sql: SQL查询语句
- limit: 返回结果数量限制，默认为100

**返回：**
- 查询结果的JSON字符串

### 4. 获取表数据
灵活查询表中的数据。

**参数：**
- table_name: 表名
- columns: 要查询的列，多个列用逗号分隔，默认为*
- where: WHERE条件语句
- order_by: 排序条件
- limit: 返回结果数量限制，默认为100

**返回：**
- 表数据的JSON字符串

## 使用示例
```python
# 获取所有表
tables = get_all_tables()

# 获取用户表的字段信息
columns = get_table_columns("users")

# 执行自定义SQL查询
results = execute_raw_query("SELECT * FROM users WHERE age > 18")

# 获取表数据
data = get_table_data("orders", columns="id,customer_name,total", where="total > 100", order_by="id DESC")
```

## 注意事项
1. 出于安全考虑，只支持执行SELECT查询
2. 查询结果默认限制为100条记录
3. 需要安装pymysql库
"""
                )
                db.add(db_utils_module)

                db.commit()
                mcp_logger.info("初始化了演示模块数据")

    except Exception as e:
        mcp_logger.error(f"初始化演示模块失败: {str(e)}")


def init_admin_users():
    """初始化管理员用户数据"""
    # 创建初始管理员用户
    from werkzeug.security import generate_password_hash
    from datetime import datetime

    try:
        with get_db() as db:
            # 检查是否已有管理员用户
            count_query = select(User).where(User.username == "admin")
            admin_count = len(db.execute(count_query).all())

            if not admin_count:
                mcp_logger.info("创建默认管理员用户")

                # 检查是否已有默认租户
                default_tenant_query = select(Tenant).where(Tenant.code == "default")
                default_tenant_count = len(db.execute(default_tenant_query).all())

                if not default_tenant_count:
                    # 创建默认租户
                    default_tenant = TenantService.create_tenant(
                        name="默认租户",
                        description="系统默认租户",
                        code="default"
                    )

                # 修改默认密码为 mcp@12345
                admin_user = UserService.create_user(
                    username="admin",
                    password="mcp@12345",  # 直接使用明文密码，由create_user内部进行哈希
                    fullname="系统管理员",
                    is_admin=True,
                    tenant_ids=[default_tenant.id]
                )
    except Exception as e:
        mcp_logger.error(f"初始化管理员用户失败: {str(e)}")
