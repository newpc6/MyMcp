"""
系统管理服务实现
"""
import sys
import platform
import psutil
import pkg_resources
import asyncio
import logging
import threading
import subprocess
import queue
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from app.utils.logging import mcp_logger


class SystemService:
    """系统管理服务类"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            # 获取Python版本
            python_version = platform.python_version()

            # 获取系统运行时间
            boot_time = psutil.boot_time()
            boot_datetime = datetime.fromtimestamp(boot_time)
            uptime = datetime.now() - boot_datetime
            uptime_str = self._format_uptime(uptime)

            # 获取MCP服务状态（简单示例）
            mcp_status = "running"  # 这里可以根据实际情况检测服务状态

            # 系统基本信息
            system_info = {
                "pythonVersion": python_version,
                "uptime": uptime_str,
                "mcpStatus": mcp_status,
                "platform": platform.platform(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "used": psutil.virtual_memory().used,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            }

            return system_info
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            raise e

    def _format_uptime(self, uptime: timedelta) -> str:
        """格式化运行时间"""
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if days > 0:
            return f"{days}天 {hours}小时 {minutes}分钟"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟"

    async def get_installed_packages(self) -> List[Dict[str, str]]:
        """获取已安装的Python包列表"""
        try:
            # 使用pkg_resources获取已安装包
            installed_packages = []
            for package in pkg_resources.working_set:
                package_info = {
                    "name": package.project_name,
                    "version": package.version,
                    "location": package.location
                }

                # 尝试获取包的摘要信息
                try:
                    metadata = package.get_metadata('METADATA')
                    if metadata:
                        lines = metadata.split('\n')
                        for line in lines:
                            if line.startswith('Summary:'):
                                summary = line.replace('Summary:', '').strip()
                                package_info["summary"] = summary
                                break
                except Exception:
                    package_info["summary"] = ""

                installed_packages.append(package_info)

            # 按名称排序
            installed_packages.sort(key=lambda x: x['name'].lower())
            return installed_packages
        except Exception as e:
            self.logger.error(f"获取包列表失败: {e}")
            raise e

    async def install_package(
        self,
        package_name: str,
        upgrade: bool = False,
        user_install: bool = False,
        index_url: str = "https://pypi.tuna.tsinghua.edu.cn/simple/"
    ) -> Dict[str, Any]:
        """安装Python包（在单独线程中执行）"""
        try:
            # 创建结果队列
            result_queue = queue.Queue()

            def install_worker():
                """安装工作线程"""
                try:
                    cmd = [sys.executable, "-m", "pip", "install"]

                    # 添加镜像源
                    if index_url:
                        cmd.extend(["-i", index_url])

                    if upgrade:
                        cmd.append("--upgrade")

                    if user_install:
                        cmd.append("--user")

                    cmd.append(package_name)

                    print(f"开始安装包: {package_name}")
                    print(f"执行命令: {' '.join(cmd)}")

                    # 设置环境变量，强制使用UTF-8编码
                    env = os.environ.copy()
                    env['PYTHONIOENCODING'] = 'utf-8'
                    env['PYTHONUTF8'] = '1'

                    # 使用subprocess.Popen来实时获取输出
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        encoding='utf-8',
                        errors='replace',  # 遇到编码错误时用替换字符
                        bufsize=1,
                        env=env
                    )

                    stdout_lines = []

                    # 实时读取输出
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            line = output.strip()
                            stdout_lines.append(line)
                            # 实时打印到控制台
                            print(f"[pip] {line}")

                    # 等待进程完成
                    return_code = process.poll()

                    # 收集完整输出
                    stdout_text = '\n'.join(stdout_lines)

                    result = {
                        "package": package_name,
                        "success": return_code == 0,
                        "stdout": stdout_text,
                        "stderr": "",
                        "returncode": return_code,
                        "index_url": index_url
                    }

                    if return_code == 0:
                        print(f"✅ 包 {package_name} 安装成功!")
                    else:
                        print(f"❌ 包 {package_name} 安装失败!")

                    result_queue.put(result)

                except Exception as e:
                    error_result = {
                        "package": package_name,
                        "success": False,
                        "stdout": "",
                        "stderr": str(e),
                        "returncode": -1,
                        "index_url": index_url
                    }
                    print(f"❌ 安装过程中发生错误: {e}")
                    result_queue.put(error_result)

            # 启动安装线程
            install_thread = threading.Thread(
                target=install_worker,
                daemon=True
            )
            install_thread.start()

            # 等待线程完成（最多等待5分钟）
            install_thread.join(timeout=300)

            if install_thread.is_alive():
                timeout_msg = (
                    f"⚠️  安装超时，包 {package_name} 安装可能仍在进行中"
                )
                print(timeout_msg)
                return {
                    "package": package_name,
                    "success": False,
                    "stdout": "",
                    "stderr": "安装超时",
                    "returncode": -1,
                    "index_url": index_url
                }

            # 获取结果
            try:
                result = result_queue.get_nowait()

                if not result["success"]:
                    error_msg = f"安装失败: {result['stderr'] or result['stdout']}"
                    raise Exception(error_msg)

                return result
            except queue.Empty:
                raise Exception("无法获取安装结果")

        except Exception as e:
            self.logger.error(f"安装包失败: {e}")
            raise e

    async def upgrade_package(
        self,
        package_name: str,
        index_url: str = "https://pypi.tuna.tsinghua.edu.cn/simple/"
    ) -> Dict[str, Any]:
        """升级Python包"""
        try:
            cmd = [
                sys.executable, "-m", "pip", "install",
                "--upgrade"
            ]

            # 添加镜像源
            if index_url:
                cmd.extend(["-i", index_url])

            cmd.append(package_name)

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            stdout_text = stdout.decode('utf-8', errors='ignore')
            stderr_text = stderr.decode('utf-8', errors='ignore')

            result = {
                "package": package_name,
                "success": process.returncode == 0,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "returncode": process.returncode,
                "index_url": index_url
            }

            if process.returncode != 0:
                error_msg = f"升级失败: {stderr_text}"
                raise Exception(error_msg)

            return result
        except Exception as e:
            self.logger.error(f"升级包失败: {e}")
            raise e

    async def uninstall_package(self, package_name: str) -> Dict[str, Any]:
        """卸载Python包"""
        try:
            cmd = [
                sys.executable, "-m", "pip", "uninstall",
                "-y", package_name
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            stdout_text = stdout.decode('utf-8', errors='ignore')
            stderr_text = stderr.decode('utf-8', errors='ignore')

            result = {
                "package": package_name,
                "success": process.returncode == 0,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "returncode": process.returncode
            }

            if process.returncode != 0:
                error_msg = f"卸载失败: {stderr_text}"
                raise Exception(error_msg)

            return result
        except Exception as e:
            self.logger.error(f"卸载包失败: {e}")
            raise e

    async def get_service_status(self) -> Dict[str, Any]:
        """获取系统服务状态"""
        try:
            # 这里可以检查各种服务的状态
            services = {
                "mcp_service": {
                    "name": "MCP服务",
                    "status": "running",
                    "uptime": "2天 5小时",
                    "pid": 1234
                },
                "database": {
                    "name": "数据库服务",
                    "status": "running",
                    "uptime": "2天 5小时",
                    "pid": 5678
                }
            }
            return services
        except Exception as e:
            self.logger.error(f"获取服务状态失败: {e}")
            raise e

    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        """重启服务"""
        try:
            # 这里实现具体的服务重启逻辑
            result = {
                "service": service_name,
                "action": "restart",
                "success": True,
                "message": f"服务 {service_name} 重启成功"
            }
            return result
        except Exception as e:
            self.logger.error(f"重启服务失败: {e}")
            raise e

    async def stop_service(self, service_name: str) -> Dict[str, Any]:
        """停止服务"""
        try:
            result = {
                "service": service_name,
                "action": "stop",
                "success": True,
                "message": f"服务 {service_name} 停止成功"
            }
            return result
        except Exception as e:
            self.logger.error(f"停止服务失败: {e}")
            raise e

    async def start_service(self, service_name: str) -> Dict[str, Any]:
        """启动服务"""
        try:
            result = {
                "service": service_name,
                "action": "start",
                "success": True,
                "message": f"服务 {service_name} 启动成功"
            }
            return result
        except Exception as e:
            self.logger.error(f"启动服务失败: {e}")
            raise e

    async def get_system_logs(
        self, level: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        """获取系统日志"""
        try:
            # 这里可以从日志文件或数据库中获取日志
            logs = []
            for i in range(limit):
                log_entry = {
                    "id": offset + i + 1,
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": f"系统日志条目 {offset + i + 1}",
                    "source": "system"
                }
                logs.append(log_entry)

            result = {
                "logs": logs,
                "total": 1000,  # 总日志数量
                "limit": limit,
                "offset": offset
            }
            return result
        except Exception as e:
            self.logger.error(f"获取系统日志失败: {e}")
            raise e

    async def clear_system_logs(self) -> Dict[str, Any]:
        """清空系统日志"""
        try:
            # 这里实现清空日志的逻辑
            result = {
                "success": True,
                "message": "系统日志已清空",
                "cleared_count": 1000
            }
            return result
        except Exception as e:
            self.logger.error(f"清空系统日志失败: {e}")
            raise e

    
    async def get_scheduled_tasks(self):
        """获取定时任务列表"""
        try:            
            import schedule
            
            # 获取所有已注册的定时任务
            tasks = []
            
            for job in schedule.jobs:
                # 获取下次执行时间
                next_run = (
                    job.next_run.strftime('%Y-%m-%d %H:%M:%S') 
                    if job.next_run else '未安排'
                )
                
                # 根据任务函数名判断任务类型
                task_name = job.job_func.__name__
                task_description = ""
                task_category = "其他"
                
                if task_name == "update_statistics":
                    task_description = "更新系统统计数据"
                    task_category = "统计"
                elif task_name == "update_daily_statistics":
                    task_description = "更新每日统计数据"
                    task_category = "统计"
                elif task_name == "clean_old_statistics":
                    task_description = "清理过期统计数据"
                    task_category = "清理"
                elif task_name == "clean_expired_cache":
                    task_description = "清理过期缓存"
                    task_category = "清理"
                else:
                    task_description = f"执行 {task_name}"
                
                # 获取执行间隔信息
                interval_desc = ""
                if hasattr(job, 'interval') and job.interval:
                    if job.unit == 'minutes':
                        interval_desc = f"每 {job.interval} 分钟"
                    elif job.unit == 'hours':
                        interval_desc = f"每 {job.interval} 小时"
                    elif job.unit == 'days':
                        interval_desc = f"每 {job.interval} 天"
                    else:
                        interval_desc = f"每 {job.interval} {job.unit}"
                elif hasattr(job, 'at_time') and job.at_time:
                    interval_desc = f"每天 {job.at_time}"
                
                tasks.append({
                    "id": f"task_{len(tasks)}",
                    "name": task_name,
                    "description": task_description,
                    "category": task_category,
                    "interval": interval_desc,
                    "next_run": next_run,
                    "status": "运行中",
                    "enabled": True
                })
            
            return tasks
            
        except Exception as e:
            mcp_logger.error(f"获取定时任务列表时出错: {str(e)}")
            raise e

    async def execute_scheduled_task(self, task_name: str):
        """手动执行定时任务"""
        try:
            # 导入定时任务函数
            if not task_name:
                raise ValueError("任务名称不能为空")

            # 导入定时任务函数
            from app.services.schedule_service.statistics_task import (
                update_statistics,
                update_daily_statistics,
                clean_old_statistics
            )
            from app.services.schedule_service.cache_clean_task import (
                clean_expired_cache
            )

            # 根据任务名称执行对应任务
            task_functions = {
                "update_statistics": update_statistics,
                "update_daily_statistics": update_daily_statistics,
                "clean_old_statistics": clean_old_statistics,
                "clean_expired_cache": clean_expired_cache
            }

            if task_name not in task_functions:
                raise ValueError(f"未知的任务: {task_name}")

            # 在后台线程中执行任务，避免阻塞请求
            import threading

            def run_task():
                try:
                    mcp_logger.info(f"手动执行定时任务: {task_name}")
                    task_functions[task_name]()
                    mcp_logger.info(f"手动执行定时任务完成: {task_name}")
                except Exception as e:
                    mcp_logger.error(
                        f"手动执行定时任务失败: {task_name}, 错误: {str(e)}"
                    )

            thread = threading.Thread(target=run_task, daemon=True)
            thread.start()

            return {
                "message": f"任务 {task_name} 已开始执行",
                "task_name": task_name,
                "executed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            mcp_logger.error(f"执行定时任务时出错: {str(e)}")
            raise e


# 创建服务实例
system_service = SystemService()
