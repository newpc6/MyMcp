from tavily import TavilyClient
from app.services.execution.decorators import record_execution


tvly_api_key = "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"


@record_execution
def search_tavily(query: str) -> str:
    """Tavily在线搜索工具"""
    tavily_client = TavilyClient(api_key=tvly_api_key)
    response = tavily_client.search(query)
    return response


@record_execution
def extract_tavily(url: str) -> str:
    """Tavily网页内容提取工具"""
    tavily_client = TavilyClient(api_key=tvly_api_key)
    response = tavily_client.extract(url)
    return response