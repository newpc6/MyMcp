from .mcp_base import mcp
from tavily import TavilyClient
from app.services.execution.decorators import record_execution
tvly_api_key = "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"

@record_execution
@mcp.tool()
def search_tavily(query: str) -> str:
    """Tavily在线搜索工具"""
    tavily_client = TavilyClient(api_key=tvly_api_key)
    response = tavily_client.search(query)
    return response

@record_execution
@mcp.tool()
def extract_tavily(url: str) -> str:
    """Tavily网页内容提取工具"""
    tavily_client = TavilyClient(api_key=tvly_api_key)
    response = tavily_client.extract(url)
    return response