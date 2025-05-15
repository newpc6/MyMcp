"""
统计服务模块

提供MCP服务和工具调用统计相关功能
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pytz import timezone
from sqlalchemy import func, desc

from app.models.engine import get_db
from app.models.statistics import (
    ServiceStatistics,
    ModuleStatistics,
    ToolStatistics,
    ServiceCallStatistics
)
from app.models.modules.mcp_services import McpService
from app.models.modules.mcp_marketplace import McpModule
from app.models.tools.tool_execution import ToolExecution
from app.utils.logging import em_logger
from app.utils.http import PageParams, PageResult


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
                # 查询总服务数
                total_services = db.query(McpService).count()
                
                # 查询各状态服务数
                running_services = db.query(McpService).filter(
                    McpService.status == "running"
                ).count()
                
                stopped_services = db.query(McpService).filter(
                    McpService.status == "stopped"
                ).count()
                
                error_services = db.query(McpService).filter(
                    McpService.status == "error"
                ).count()
                
                # 获取或创建统计记录
                stats = db.query(ServiceStatistics).first()
                if not stats:
                    stats = ServiceStatistics()
                    db.add(stats)
                
                # 更新统计数据
                stats.total_services = total_services
                stats.running_services = running_services
                stats.stopped_services = stopped_services
                stats.error_services = error_services
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
                # 获取每个模块的服务数量
                module_stats = {}
                services = db.query(
                    McpService.module_id,
                    func.count(McpService.id).label('service_count')
                ).group_by(McpService.module_id).all()
                
                for module_id, service_count in services:
                    module_stats[module_id] = service_count
                
                # 获取所有模块
                modules = db.query(McpModule).all()
                result = []
                
                for module in modules:
                    # 查找或创建统计记录
                    stats = db.query(ModuleStatistics).filter(
                        ModuleStatistics.module_id == module.id
                    ).first()
                    
                    if not stats:
                        stats = ModuleStatistics(
                            module_id=module.id,
                            module_name=module.name,
                            user_id=module.user_id,
                            user_name=module.to_dict().get("creator_name")
                        )
                        db.add(stats)
                    
                    # 更新模块名称（可能已更改）
                    stats.module_name = module.name  # 保持名称同步
                    
                    # 更新服务数量
                    stats.service_count = module_stats.get(module.id, 0)
                    
                    # 更新创建者信息
                    stats.user_id = module.user_id
                    stats.user_name = module.to_dict().get("creator_name")
                    
                    # 更新时间
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
    
    def update_service_call_statistics(self) -> List[ServiceCallStatistics]:
        """
        更新服务调用统计数据
        
        Returns:
            List[ServiceCallStatistics]: 更新后的服务调用统计数据列表
        """
        with get_db() as db:
            try:
                # 获取所有有调用记录的服务ID
                service_ids = db.query(ToolExecution.service_id).filter(
                    ToolExecution.service_id.isnot(None)
                ).distinct().all()
                
                result = []
                
                for (service_id,) in service_ids:
                    # 基础查询
                    base_query = db.query(ToolExecution).filter(
                        ToolExecution.service_id == service_id
                    )
                    
                    # 统计数据
                    call_count = base_query.count()
                    success_count = base_query.filter(
                        ToolExecution.status == 'success'
                    ).count()
                    error_count = base_query.filter(
                        ToolExecution.status == 'error'
                    ).count()
                    
                    # 获取服务信息
                    service = db.query(McpService).filter(
                        McpService.id == service_id
                    ).first()
                    
                    service_name = "未知服务"
                    module_name = "未知模块"
                    
                    if service:
                        service_name = service.name or f"服务 {service_id}"
                        
                        # 获取模块信息
                        if service.module_id:
                            module = db.query(McpModule).filter(
                                McpModule.id == service.module_id
                            ).first()
                            if module:
                                module_name = module.name
                    
                    # 查找或创建统计记录
                    stats = db.query(ServiceCallStatistics).filter(
                        ServiceCallStatistics.service_id == service_id
                    ).first()
                    
                    if not stats:
                        stats = ServiceCallStatistics(
                            service_id=service_id,
                            service_name=service_name,
                            module_name=module_name
                        )
                        db.add(stats)
                    
                    # 更新统计数据
                    stats.service_name = service_name
                    stats.module_name = module_name
                    stats.call_count = call_count
                    stats.success_count = success_count
                    stats.error_count = error_count
                    stats.updated_at = datetime.now(timezone('Asia/Shanghai'))
                    
                    result.append(stats)
                
                db.commit()
                for stats in result:
                    db.refresh(stats)
                
                return result
            except Exception as e:
                db.rollback()
                em_logger.error(f"更新服务调用统计数据时出错: {str(e)}")
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
    
    def get_module_rankings(self, size: int = 10, page: int = 1) -> Dict[str, Any]:
        """
        获取模块发布排名

        Args:
            size: 每页数量限制
            page: 页码
            
        Returns:
            Dict[str, Any]: 分页的模块排名数据
        """
        with get_db() as db:
            try:
                # 创建分页参数
                page_params = PageParams(
                    page=page, 
                    size=size, 
                    offset=(page - 1) * size
                )
                
                # 构建查询
                query = db.query(ModuleStatistics).order_by(
                    ModuleStatistics.service_count.desc()
                )
                
                # 使用通用分页功能获取结果
                result = PageResult.from_query(query, page_params)
                
                # 转换为字典格式
                return {
                    "items": [stat.to_dict() for stat in result.items],
                    "total": result.total,
                    "page": result.page,
                    "size": result.size,
                    "pages": result.total_pages
                }
            except Exception as e:
                em_logger.error(f"获取模块排名数据时出错: {str(e)}")
                raise

    def get_tool_rankings(self, size: int = 10, page: int = 1) -> Dict[str, Any]:
        """
        获取工具调用排名

        Args:
            size: 每页数量限制
            page: 页码
            
        Returns:
            Dict[str, Any]: 分页的工具排名数据
        """
        with get_db() as db:
            try:
                # 创建分页参数
                page_params = PageParams(
                    page=page, 
                    size=size, 
                    offset=(page - 1) * size
                )
                
                # 构建查询
                query = db.query(ToolStatistics).order_by(
                    ToolStatistics.call_count.desc()
                )
                
                # 使用通用分页功能获取结果
                result = PageResult.from_query(query, page_params)
                
                # 转换为字典格式
                return {
                    "items": [stat.to_dict() for stat in result.items],
                    "total": result.total,
                    "page": result.page,
                    "size": result.size,
                    "pages": result.total_pages
                }
            except Exception as e:
                em_logger.error(f"获取工具排名数据时出错: {str(e)}")
                raise

    def get_service_rankings(self, size: int = 10, page: int = 1) -> Dict[str, Any]:
        """
        获取服务调用排名

        Args:
            size: 每页数量限制
            page: 页码
            
        Returns:
            Dict[str, Any]: 分页的服务排名数据
        """
        with get_db() as db:
            try:
                # 创建分页参数
                page_params = PageParams(
                    page=page, 
                    size=size, 
                    offset=(page - 1) * size
                )
                
                # 构建查询
                query = db.query(ServiceCallStatistics).order_by(
                    ServiceCallStatistics.call_count.desc()
                )
                
                # 使用通用分页功能获取结果
                result = PageResult.from_query(query, page_params)
                
                # 转换为字典格式
                return {
                    "items": [stat.to_dict() for stat in result.items],
                    "total": result.total,
                    "page": result.page,
                    "size": result.size,
                    "pages": result.total_pages
                }
            except Exception as e:
                em_logger.error(f"获取服务排名数据时出错: {str(e)}")
                raise
    
    def get_tool_executions(
        self, 
        page: int = 1, 
        size: int = 20, 
        tool_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取工具执行记录（分页）
        
        Args:
            page: 页码
            size: 每页记录数
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
            
            # 创建分页参数
            page_params = PageParams(
                page=page, 
                size=size, 
                offset=(page - 1) * size
            )
            
            # 应用排序
            query = query.order_by(desc(ToolExecution.created_at))
            # 使用通用分页功能获取结果
            result = PageResult.from_query(query, page_params)
            
            # 转换为字典列表
            items = []
            
            # 获取所有涉及的模块ID和服务ID
            module_ids = {
                ex.module_id for ex in result.items 
                if ex.module_id is not None
            }
            service_ids = {
                ex.service_id for ex in result.items 
                if ex.service_id is not None
            }
            
            # 一次性查询所有相关模块
            modules = {}
            if module_ids:
                module_records = db.query(McpModule).filter(
                    McpModule.id.in_(module_ids)
                ).all()
                modules = {m.id: m for m in module_records}
            
            # 一次性查询所有相关服务
            services = {}
            if service_ids:
                service_records = db.query(McpService).filter(
                    McpService.id.in_(service_ids)
                ).all()
                services = {s.id: s for s in service_records}
            
            for ex in result.items:
                # 获取关联的模块信息
                module_info = {}
                creator_name = None
                if ex.module_id and ex.module_id in modules:
                    module = modules[ex.module_id]
                    module_info = {
                        "id": module.id,
                        "name": module.name,
                        "description": module.description
                    }
                    creator_name = module.to_dict().get("creator_name")
                
                # 获取关联的服务信息
                service_info = {}
                if ex.service_id and ex.service_id in services:
                    service = services[ex.service_id]
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
                    result_json = json.loads(ex.result) if ex.result else None
                except json.JSONDecodeError:
                    result_json = {"raw": ex.result}
                
                items.append({
                    "id": ex.id,
                    "tool_name": ex.tool_name,
                    "service_id": ex.service_id,
                    "module_id": ex.module_id,
                    "service": service_info,
                    "module": module_info,
                    "creator_name": creator_name,
                    "description": ex.description,
                    "parameters": parameters,
                    "result": result_json,
                    "status": ex.status,
                    "execution_time": ex.execution_time,
                    "created_at": ex.created_at.isoformat()
                })
            
            # 将转换后的字典列表赋值给result.items
            result.items = items
            
            # 返回分页结果
            return result.to_dict()
    
    def get_tool_executions_by_module(
        self,
        page: int = 1,
        size: int = 20,
        module_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取按模块分组的工具执行记录（分页）
        
        Args:
            page: 页码
            size: 每页记录数
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
            
            # 创建分页参数
            page_params = PageParams(
                page=page, 
                size=size, 
                offset=(page - 1) * size
            )
            
            # 应用排序
            query = query.order_by(desc(ToolExecution.created_at))
            
            # 获取总记录数和分页后的数据
            total = query.count()
            executions = query.offset(page_params.offset).limit(page_params.size).all()
            
            # 转换为字典列表
            items = []
            
            # 获取所有涉及的模块ID和服务ID
            module_ids = {
                ex.module_id for ex in executions 
                if ex.module_id is not None
            }
            service_ids = {
                ex.service_id for ex in executions 
                if ex.service_id is not None
            }
            
            # 一次性查询所有相关模块
            modules = {}
            if module_ids:
                module_records = db.query(McpModule).filter(
                    McpModule.id.in_(module_ids)
                ).all()
                modules = {m.id: m for m in module_records}
            
            # 一次性查询所有相关服务
            services = {}
            if service_ids:
                service_records = db.query(McpService).filter(
                    McpService.id.in_(service_ids)
                ).all()
                services = {s.id: s for s in service_records}
            
            for ex in executions:
                # 获取关联的模块信息
                module_info = {}
                if ex.module_id and ex.module_id in modules:
                    module = modules[ex.module_id]
                    module_info = {
                        "id": module.id,
                        "name": module.name,
                        "description": module.description
                    }
                
                # 获取关联的服务信息（添加到字典中，但此方法不在输出中使用）
                # 此变量仍保留以便将来可能的扩展
                service_info = {}
                if ex.service_id and ex.service_id in services:
                    service = services[ex.service_id]
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
                    result_json = json.loads(ex.result) if ex.result else None
                except json.JSONDecodeError:
                    result_json = {"raw": ex.result}
                
                items.append({
                    "id": ex.id,
                    "tool_name": ex.tool_name,
                    "module_id": ex.module_id,
                    "module": module_info,
                    "description": ex.description,
                    "parameters": parameters,
                    "result": result_json,
                    "status": ex.status,
                    "execution_time": ex.execution_time,
                    "created_at": ex.created_at.isoformat()
                })
            
            # 计算总页数
            total_pages = ((total + page_params.size - 1) // page_params.size
                           if total > 0 else 0)
            
            # 返回分页结果
            return {
                "items": items,
                "total": total,
                "page": page_params.page,
                "size": page_params.size,
                "pages": total_pages
            }
    
    def get_tool_executions_by_service(
        self,
        page: int = 1,
        size: int = 20,
        service_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取按服务分组的工具执行记录（分页）
        
        Args:
            page: 页码
            size: 每页记录数
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
            
            # 创建分页参数
            page_params = PageParams(
                page=page, 
                size=size, 
                offset=(page - 1) * size
            )
            
            # 应用排序
            query = query.order_by(desc(ToolExecution.created_at))
            
            # 获取总记录数和分页后的数据
            total = query.count()
            executions = (query.offset(page_params.offset)
                         .limit(page_params.size).all())
            
            # 转换为字典列表
            items = []
            
            # 获取所有涉及的模块ID和服务ID
            module_ids = {
                ex.module_id for ex in executions 
                if ex.module_id is not None
            }
            service_ids = {
                ex.service_id for ex in executions 
                if ex.service_id is not None
            }
            
            # 一次性查询所有相关模块
            modules = {}
            if module_ids:
                module_records = db.query(McpModule).filter(
                    McpModule.id.in_(module_ids)
                ).all()
                modules = {m.id: m for m in module_records}
            
            # 一次性查询所有相关服务
            services = {}
            if service_ids:
                service_records = db.query(McpService).filter(
                    McpService.id.in_(service_ids)
                ).all()
                services = {s.id: s for s in service_records}
            
            for ex in executions:
                # 获取关联的模块信息
                module_info = {}
                if ex.module_id and ex.module_id in modules:
                    module = modules[ex.module_id]
                    module_info = {
                        "id": module.id,
                        "name": module.name,
                        "description": module.description
                    }
                
                # 获取关联的服务信息
                service_info = {}
                if ex.service_id and ex.service_id in services:
                    service = services[ex.service_id]
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
                    result_json = json.loads(ex.result) if ex.result else None
                except json.JSONDecodeError:
                    result_json = {"raw": ex.result}
                
                items.append({
                    "id": ex.id,
                    "tool_name": ex.tool_name,
                    "service_id": ex.service_id,
                    "service": service_info,
                    "module_id": ex.module_id,
                    "module": module_info,
                    "description": ex.description,
                    "parameters": parameters,
                    "result": result_json,
                    "status": ex.status,
                    "execution_time": ex.execution_time,
                    "created_at": ex.created_at.isoformat()
                })
            
            # 计算总页数
            total_pages = ((total + page_params.size - 1) // page_params.size
                           if total > 0 else 0)
            
            # 返回分页结果
            return {
                "items": items,
                "total": total,
                "page": page_params.page,
                "size": page_params.size,
                "pages": total_pages
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
    
    def refresh_all_statistics(self) -> Dict[str, Any]:
        """
        刷新所有统计数据
        
        Returns:
            Dict: 刷新结果
        """
        try:
            # 更新服务统计
            service_stats = self.update_service_statistics()
            
            # 更新模块统计
            module_stats = self.update_module_statistics()
            
            # 更新工具统计
            tool_stats = self.update_tool_statistics()
            
            # 更新服务调用统计
            service_call_stats = self.update_service_call_statistics()
            
            return {
                "service_stats": service_stats.total_services,
                "module_stats": len(module_stats),
                "tool_stats": len(tool_stats),
                "service_call_stats": len(service_call_stats),
                "updated_at": (datetime.now(timezone('Asia/Shanghai'))
                               .isoformat())
            }
        except Exception as e:
            em_logger.error(f"刷新统计数据时出错: {str(e)}")
            raise


# 创建统计服务实例
statistics_service = StatisticsService() 