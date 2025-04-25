"""
统计服务模块

提供MCP服务和工具调用统计相关功能
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pytz import timezone
from sqlalchemy import func, desc, case
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.models.engine import get_db
from app.models.statistics import (
    ServiceStatistics,
    ModuleStatistics,
    ToolStatistics
)
from app.models.modules.mcp_services import McpService
from app.models.modules.mcp_marketplace import McpModule
from app.models.tools.tool_execution import ToolExecution
from app.models.modules.users import User
from app.utils.logging import em_logger


class StatisticsService:
    """统计服务，提供MCP服务和工具调用统计功能"""

    def __init__(self):
        """初始化统计服务"""
        pass

    def update_service_statistics(self) -> ServiceStatistics:
        """
        更新服务统计数据

        Returns:
            ServiceStatistics: 更新后的服务统计数据
        """
        with get_db() as db:
            try:
                # 获取服务状态统计
                total_count = db.query(McpService).count()
                running_count = db.query(McpService).filter(
                    McpService.status == "running"
                ).count()
                stopped_count = db.query(McpService).filter(
                    McpService.status == "stopped"
                ).count()
                error_count = db.query(McpService).filter(
                    McpService.status == "error"
                ).count()

                # 获取或创建统计记录
                stats = db.query(ServiceStatistics).first()
                if not stats:
                    stats = ServiceStatistics()
                    db.add(stats)

                # 更新统计数据
                stats.total_services = total_count
                stats.running_services = running_count
                stats.stopped_services = stopped_count
                stats.error_services = error_count
                stats.updated_at = datetime.now(timezone('Asia/Shanghai'))

                db.commit()
                db.refresh(stats)

                return stats
            except Exception as e:
                db.rollback()
                em_logger.error(f"更新服务统计数据时出错: {str(e)}")
                raise

    def update_module_statistics(self) -> List[ModuleStatistics]:
        """
        更新模块统计数据

        Returns:
            List[ModuleStatistics]: 更新后的模块统计数据列表
        """
        with get_db() as db:
            try:
                # 获取模块服务数量统计
                module_stats = {}
                services = db.query(
                    McpService.module_id,
                    func.count(McpService.id).label('service_count')
                ).group_by(McpService.module_id).all()

                for module_id, service_count in services:
                    module_stats[module_id] = service_count

                # 获取所有模块
                modules = db.query(McpModule).all()

                # 更新或创建模块统计记录
                result = []
                users = db.query(User).all()
                user_map = {user.id: user for user in users}
                for module in modules:
                    # 查找现有统计或创建新统计
                    stats = db.query(ModuleStatistics).filter(
                        ModuleStatistics.module_id == module.id
                    ).first()
                    # 检查用户名
                    user = user_map.get(module.user_id)
                    user_name = '管理员'
                    if user and hasattr(user, 'username'):
                        user_name = user.username
                    if not stats:
                        stats = ModuleStatistics(
                            module_id=module.id,
                            module_name=module.name,
                            user_id=module.user_id,
                            user_name=user_name
                        )
                        db.add(stats)
                    # 更新统计数据
                    stats.service_count = module_stats.get(module.id, 0)
                    stats.module_name = module.name  # 保持名称同步
                    stats.user_name = user_name
                    stats.user_id = module.user_id
                    stats.updated_at = datetime.now(timezone('Asia/Shanghai'))
                    
                    result.append(stats)
                
                db.commit()
                for stats in result:
                    db.refresh(stats)
                
                return result
            except Exception as e:
                db.rollback()
                em_logger.error(f"更新模块统计数据时出错: {str(e)}")
                raise
    
    def update_tool_statistics(self) -> List[ToolStatistics]:
        """
        更新工具调用统计数据
        
        Returns:
            List[ToolStatistics]: 更新后的工具统计数据列表
        """
        with get_db() as db:
            try:
                # 获取所有工具名称
                tool_names = db.query(ToolExecution.tool_name).distinct().all()
                result = []
                
                for (tool_name,) in tool_names:
                    # 基础查询
                    base_query = db.query(ToolExecution).filter(
                        ToolExecution.tool_name == tool_name
                    )
                    
                    # 统计数据
                    call_count = base_query.count()
                    success_count = base_query.filter(
                        ToolExecution.status == 'success'
                    ).count()
                    error_count = base_query.filter(
                        ToolExecution.status == 'error'
                    ).count()
                    
                    # 计算平均执行时间
                    avg_time_result = db.query(
                        func.avg(ToolExecution.execution_time)
                    ).filter(
                        ToolExecution.tool_name == tool_name
                    ).scalar()
                    avg_time = int(avg_time_result) if avg_time_result else 0
                    
                    # 获取最后调用时间
                    last_called = db.query(
                        ToolExecution.created_at
                    ).filter(
                        ToolExecution.tool_name == tool_name
                    ).order_by(
                        desc(ToolExecution.created_at)
                    ).first()
                    last_called = last_called[0] if last_called else None
                    
                    # 查找或创建统计记录
                    stats = db.query(ToolStatistics).filter(
                        ToolStatistics.tool_name == tool_name
                    ).first()
                    
                    if not stats:
                        stats = ToolStatistics(tool_name=tool_name)
                        db.add(stats)
                    
                    # 更新统计数据
                    stats.call_count = call_count
                    stats.success_count = success_count
                    stats.error_count = error_count
                    stats.avg_execution_time = avg_time
                    stats.last_called_at = last_called
                    stats.updated_at = datetime.now(timezone('Asia/Shanghai'))
                    
                    result.append(stats)
                
                db.commit()
                for stats in result:
                    db.refresh(stats)
                
                return result
            except Exception as e:
                db.rollback()
                em_logger.error(f"更新工具统计数据时出错: {str(e)}")
                raise
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """
        获取服务统计数据
        
        Returns:
            Dict: 服务统计数据
        """
        # 首先更新统计数据
        stats = self.update_service_statistics()
        
        # 返回统计结果
        return {
            "total_services": stats.total_services,
            "running_services": stats.running_services,
            "stopped_services": stats.stopped_services,
            "error_services": stats.error_services,
            "updated_at": stats.updated_at.isoformat()
        }
    
    def get_module_rankings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取模块发布排名
        
        Args:
            limit: 返回结果数量限制
            
        Returns:
            List[Dict]: 模块排名数据列表
        """
        # 首先更新统计数据
        self.update_module_statistics()
        
        with get_db() as db:
            # 查询排名数据
            rankings = db.query(ModuleStatistics).order_by(
                desc(ModuleStatistics.service_count)
            ).limit(limit).all()
        
            # 转换为字典列表
            return [
                {
                    "module_id": r.module_id,
                    "module_name": r.module_name,
                    "service_count": r.service_count,
                    "user_id": r.user_id,
                    "user_name": r.user_name,
                    "updated_at": r.updated_at.isoformat()
                }
                for r in rankings
            ]
    
    def get_tool_rankings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取工具调用排名
        
        Args:
            limit: 返回结果数量限制
            
        Returns:
            List[Dict]: 工具排名数据列表
        """
        # 首先更新统计数据
        self.update_tool_statistics()
        
        with get_db() as db:
            # 查询排名数据
            rankings = db.query(ToolStatistics).order_by(
                desc(ToolStatistics.call_count)
            ).limit(limit).all()
        
            # 转换为字典列表
            return [
                {
                    "tool_name": r.tool_name,
                    "call_count": r.call_count,
                    "success_count": r.success_count,
                    "error_count": r.error_count,
                    "avg_execution_time": r.avg_execution_time,
                    "last_called_at": (
                        r.last_called_at.isoformat() 
                        if r.last_called_at else None
                    ),
                    "updated_at": r.updated_at.isoformat()
                }
                for r in rankings
            ]
    
    def get_tool_executions(
        self, 
        page: int = 1, 
        per_page: int = 20, 
        tool_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取工具执行记录（分页）
        
        Args:
            page: 页码
            per_page: 每页记录数
            tool_name: 工具名称过滤
            
        Returns:
            Dict: 包含分页工具执行记录的字典
        """
        with get_db() as db:
            # 构建查询
            query = db.query(ToolExecution)
                
            # 应用过滤器
            if tool_name:
                query = query.filter(ToolExecution.tool_name == tool_name)
            
            # 获取总记录数
            total = query.count()
            
            # 计算分页
            offset = (page - 1) * per_page
            
            # 获取分页数据
            executions = query.order_by(
                desc(ToolExecution.created_at)
            ).offset(offset).limit(per_page).all()
            
            # 转换为字典列表
            items = []
            for ex in executions:
                # 解析参数和结果
                try:
                    parameters = (
                        json.loads(ex.parameters) if ex.parameters else {}
                    )
                except json.JSONDecodeError:
                    parameters = {"raw": ex.parameters}
                
                try:
                    result = json.loads(ex.result) if ex.result else None
                except json.JSONDecodeError:
                    result = {"raw": ex.result}
                
                items.append({
                    "id": ex.id,
                    "tool_name": ex.tool_name,
                    "description": ex.description,
                    "parameters": parameters,
                    "result": result,
                    "status": ex.status,
                    "execution_time": ex.execution_time,
                    "created_at": ex.created_at.isoformat()
                })
            
            # 返回分页结果
            return {
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }

    def get_tool_executions_by_module(
        self,
        page: int = 1,
        per_page: int = 20,
        module_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取按模块分组的工具执行记录（分页）
        
        Args:
            page: 页码
            per_page: 每页记录数
            module_id: 模块ID过滤
            
        Returns:
            Dict: 包含分页工具执行记录的字典
        """
        with get_db() as db:
            # 构建查询
            query = db.query(ToolExecution)
                
            # 应用过滤器
            if module_id:
                query = query.filter(ToolExecution.module_id == module_id)
            else:
                # 只查询有模块ID的记录
                query = query.filter(ToolExecution.module_id.isnot(None))
            
            # 获取总记录数
            total = query.count()
            
            # 计算分页
            offset = (page - 1) * per_page
            
            # 获取分页数据
            executions = query.order_by(
                desc(ToolExecution.created_at)
            ).offset(offset).limit(per_page).all()
            
            # 转换为字典列表
            items = []
            for ex in executions:
                # 获取关联的模块信息
                module_info = {}
                if ex.module_id:
                    module = db.query(McpModule).filter(
                        McpModule.id == ex.module_id
                    ).first()
                    if module:
                        module_info = {
                            "id": module.id,
                            "name": module.name,
                            "description": module.description
                        }
                
                # 解析参数和结果
                try:
                    parameters = (
                        json.loads(ex.parameters) if ex.parameters else {}
                    )
                except json.JSONDecodeError:
                    parameters = {"raw": ex.parameters}
                
                try:
                    result = json.loads(ex.result) if ex.result else None
                except json.JSONDecodeError:
                    result = {"raw": ex.result}
                
                items.append({
                    "id": ex.id,
                    "tool_name": ex.tool_name,
                    "module_id": ex.module_id,
                    "module": module_info,
                    "description": ex.description,
                    "parameters": parameters,
                    "result": result,
                    "status": ex.status,
                    "execution_time": ex.execution_time,
                    "created_at": ex.created_at.isoformat()
                })
            
            # 返回分页结果
            return {
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }
    
    def get_tool_executions_by_service(
        self,
        page: int = 1,
        per_page: int = 20,
        service_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取按服务分组的工具执行记录（分页）
        
        Args:
            page: 页码
            per_page: 每页记录数
            service_id: 服务ID过滤
            
        Returns:
            Dict: 包含分页工具执行记录的字典
        """
        with get_db() as db:
            # 构建查询
            query = db.query(ToolExecution)
                
            # 应用过滤器
            if service_id:
                query = query.filter(ToolExecution.service_id == service_id)
            else:
                # 只查询有服务ID的记录
                query = query.filter(ToolExecution.service_id.isnot(None))
            
            # 获取总记录数
            total = query.count()
            
            # 计算分页
            offset = (page - 1) * per_page
            
            # 获取分页数据
            executions = query.order_by(
                desc(ToolExecution.created_at)
            ).offset(offset).limit(per_page).all()
            
            # 转换为字典列表
            items = []
            for ex in executions:
                # 获取关联的服务信息
                service_info = {}
                if ex.service_id:
                    service = db.query(McpService).filter(
                        McpService.id == ex.service_id
                    ).first()
                    if service:
                        service_info = {
                            "id": service.id,
                            "name": service.name,
                            "description": service.description
                        }
                
                # 解析参数和结果
                try:
                    parameters = (
                        json.loads(ex.parameters) if ex.parameters else {}
                    )
                except json.JSONDecodeError:
                    parameters = {"raw": ex.parameters}
                
                try:
                    result = json.loads(ex.result) if ex.result else None
                except json.JSONDecodeError:
                    result = {"raw": ex.result}
                
                items.append({
                    "id": ex.id,
                    "tool_name": ex.tool_name,
                    "service_id": ex.service_id,
                    "service": service_info,
                    "description": ex.description,
                    "parameters": parameters,
                    "result": result,
                    "status": ex.status,
                    "execution_time": ex.execution_time,
                    "created_at": ex.created_at.isoformat()
                })
            
            # 返回分页结果
            return {
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }
                
    def get_module_tool_rankings(
        self, 
        module_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取特定模块的工具调用排名
        
        Args:
            module_id: 模块ID
            limit: 返回结果数量限制
            
        Returns:
            List[Dict]: 工具排名数据列表
        """
        with get_db() as db:
            # 查询统计数据
            tool_stats = db.query(
                ToolExecution.tool_name,
                func.count(ToolExecution.id).label('count')
            ).filter(
                ToolExecution.module_id == module_id
            ).group_by(
                ToolExecution.tool_name
            ).order_by(
                desc('count')
            ).limit(limit).all()
            
            # 转换为字典列表
            return [
                {
                    "tool_name": tool_name,
                    "count": count
                }
                for tool_name, count in tool_stats
            ]


# 创建服务实例
statistics_service = StatisticsService() 