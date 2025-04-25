import time
from typing import Dict, Any
import importlib
from ...core.config import settings
from ..tools.service import ToolService
from ..history.service import HistoryService


class ExecutionService:
    def __init__(self):
        self.base_dir = settings.MCP_BASE_DIR
        self.modules = settings.MCP_MODULES
        self.tool_service = ToolService()
        self.history_service = HistoryService()

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """执行MCP工具"""
        tools = self.tool_service.scan_tools()
        
        if tool_name not in tools:
            raise ValueError(f"工具 {tool_name} 不存在")
        
        tool_info = tools[tool_name]
        module_name = tool_info["module"]
        
        # if module_name not in self.modules:
        #     raise ValueError(f"模块 {module_name} 不在缓存中")
        
        # module = self.modules[module_name]
        module = importlib.import_module(module_name)
        tool_func = getattr(module, tool_name)
        
        try:
            # start_time = time.time()
            ret = tool_func(**parameters)
            execution_time = time.time() - start_time
            self.history_service.record_tool_execution(
                tool_name=tool_name,
                description=tool_info["doc"],
                parameters=parameters,
                result=ret,
                status="success",
                execution_time=execution_time
            )
            return ret
        except Exception as e:
            raise RuntimeError(f"执行错误: {str(e)}")