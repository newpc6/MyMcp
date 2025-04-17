import os
import subprocess
import time
import psutil
from datetime import datetime, timedelta

from ...models.protocols.schemas import McpServiceInfo, McpServiceActionResult
from ...config import settings


class McpServiceManager:
    """MCP服务管理器"""

    def __init__(self):
        self.mcp_service_cmd = settings.MCP_SERVICE_CMD
        self.mcp_service_pid_file = settings.MCP_SERVICE_PID_FILE
        self.mcp_version = settings.MCP_VERSION

    def get_service_info(self) -> McpServiceInfo:
        """获取MCP服务状态信息"""
        status = "stopped"
        uptime = "00:00:00"
        connection_count = 0
        
        # 检查服务是否运行
        pid = self._get_service_pid()
        if pid and self._is_pid_running(pid):
            status = "running"
            # 获取进程启动时间
            try:
                process = psutil.Process(pid)
                start_time = datetime.fromtimestamp(process.create_time())
                uptime_delta = datetime.now() - start_time
                uptime = str(timedelta(seconds=int(uptime_delta.total_seconds())))
                
                # 获取连接数
                connections = process.connections()
                connection_count = len(connections)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                status = "error"
        
        return McpServiceInfo(
            status=status,
            uptime=uptime,
            version=self.mcp_version,
            connectionCount=connection_count
        )

    def start_service(self) -> McpServiceActionResult:
        """启动MCP服务"""
        # 检查服务是否已经运行
        pid = self._get_service_pid()
        if pid and self._is_pid_running(pid):
            return McpServiceActionResult(
                success=False,
                message="MCP服务已经在运行中"
            )
        
        try:
            # 启动服务
            subprocess.Popen(
                self.mcp_service_cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # 等待服务启动
            for _ in range(5):  # 最多等待5秒
                time.sleep(1)
                pid = self._get_service_pid()
                if pid and self._is_pid_running(pid):
                    return McpServiceActionResult(
                        success=True,
                        message="MCP服务已成功启动"
                    )
            
            return McpServiceActionResult(
                success=False,
                message="MCP服务启动超时，请检查日志"
            )
        except Exception as e:
            return McpServiceActionResult(
                success=False,
                message=f"启动MCP服务失败: {str(e)}"
            )

    def stop_service(self) -> McpServiceActionResult:
        """停止MCP服务"""
        pid = self._get_service_pid()
        if not pid or not self._is_pid_running(pid):
            return McpServiceActionResult(
                success=False,
                message="MCP服务未运行"
            )
        
        try:
            # 尝试正常终止进程
            process = psutil.Process(pid)
            process.terminate()
            
            # 等待进程终止
            gone, alive = psutil.wait_procs([process], timeout=3)
            if alive:
                # 如果进程仍然存活，强制终止
                for p in alive:
                    p.kill()
            
            # 删除PID文件
            if os.path.exists(self.mcp_service_pid_file):
                os.remove(self.mcp_service_pid_file)
            
            return McpServiceActionResult(
                success=True,
                message="MCP服务已成功停止"
            )
        except Exception as e:
            return McpServiceActionResult(
                success=False,
                message=f"停止MCP服务失败: {str(e)}"
            )

    def restart_service(self) -> McpServiceActionResult:
        """重启MCP服务"""
        stop_result = self.stop_service()
        if not stop_result.success:
            # 如果服务未运行，仍然继续启动
            if "MCP服务未运行" not in stop_result.message:
                return stop_result
        
        # 等待一段时间，确保服务完全停止
        time.sleep(2)
        
        # 启动服务
        return self.start_service()

    def _get_service_pid(self) -> int:
        """从PID文件获取服务进程ID"""
        try:
            if os.path.exists(self.mcp_service_pid_file):
                with open(self.mcp_service_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                    return pid
        except (IOError, ValueError):
            pass
        return None

    def _is_pid_running(self, pid) -> bool:
        """检查进程是否运行"""
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False 