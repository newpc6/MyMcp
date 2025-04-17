import os
import webbrowser
import urllib.parse

# 使用绝对导入
from .mcp_base import mcp
from app.services.execution.decorators import record_execution

@record_execution
@mcp.tool()
def list_desktop_files() -> list:
    """获取当前用户桌面上的所有文件列表"""
    desktop_path = os.path.expanduser("~/Desktop")
    return os.listdir(desktop_path)

@record_execution
@mcp.tool()
def say_hello(name: str) -> str:
    """生成个性化问候语"""
    return f"  你好 {name}! (Hello {name}!)"

@mcp.resource("config://app_settings")
def get_app_config() -> dict:
    return {"theme": "dark", "language": "zh-CN"}

@mcp.prompt()
def code_review_prompt(code: str) -> str:
    return f"请审查以下代码并指出问题：\n\n{code}"

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    result = a + b
    print('add')
    # 在函数内部直接记录执行
    from app.services.execution.utils import record_tool_call
    record_tool_call(
        func_name="add", 
        description="Add two numbers",
        parameters={"a": a, "b": b},
        result=result
    )
    
    return result

@record_execution
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)

@mcp.tool()
def process_chrome(query: str) -> str:
    """打开Chrome浏览器并搜索指定的问题"""
    # 将搜索词编码为URL安全的格式
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.baidu.com/s?wd={encoded_query}"
    
    # 打开默认浏览器并搜索
    webbrowser.open(search_url)
    
    result = f"已在浏览器中搜索: {query}"
    
    # 在函数内部直接记录执行
    from app.services.execution.utils import record_tool_call
    record_tool_call(
        func_name="process_chrome", 
        description="打开Chrome浏览器并搜索指定的问题",
        parameters={"query": query},
        result=result
    )
    
    return result

# if __name__ == "__main__":
#     mcp.run(transport='sse')