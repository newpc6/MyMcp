from typing import Dict, Any, Optional
import json
from sqlalchemy import desc, func
import time
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.models.engine import engine, get_db
from app.models.tools.tool_execution import ToolExecution
from sqlalchemy.orm import sessionmaker
from app.utils.logging import mcp_logger

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class HistoryService:
    """工具调用历史记录服务"""

    def __init__(self):
        """初始化数据库会话"""
        self.db = SessionLocal()
        
    def __del__(self):
        """关闭数据库会话"""
        try:
            self.db.close()
        except Exception:
            pass

    def _ensure_db_connection(self):
        """确保数据库连接有效，如果无效则重新创建"""
        try:
            # 尝试进行一个简单查询来验证连接
            self.db.execute("SELECT 1")
        except Exception:
            # 如果连接无效，尝试关闭并重新创建
            try:
                self.db.close()
            except Exception:
                pass
            self.db = SessionLocal()

    def record_tool_execution(
        self, 
        tool_name: str, 
        description: str, 
        parameters: Dict[str, Any], 
        result: Any, 
        status: str, 
        execution_time: int,
        service_id: Optional[str] = None,
        module_id: Optional[int] = None
    ) -> Optional[ToolExecution]:
        """记录工具执行"""
        # 最大重试次数
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 确保连接有效
                self._ensure_db_connection()
                
                # 创建记录
                db_record = ToolExecution(
                    tool_name=tool_name,
                    service_id=service_id,
                    module_id=module_id,
                    description=description,
                    parameters=json.dumps(parameters),
                    result=json.dumps(result) if result is not None else None,
                    status=status,
                    execution_time=execution_time
                )
                
                # 使用上下文管理器确保事务正确处理
                with get_db() as session:
                    session.add(db_record)
                    session.commit()
                    session.refresh(db_record)
                    return db_record
                    
            except OperationalError as e:
                retry_count += 1
                mcp_logger.warning(
                    f"数据库连接错误，正在进行第 {retry_count} 次重试: {str(e)}"
                )
                
                # 如果达到最大重试次数，记录错误并返回
                if retry_count >= max_retries:
                    mcp_logger.error(f"记录工具执行失败，已达到最大重试次数: {str(e)}")
                    return None
                    
                # 重试前等待一段时间
                time.sleep(1)
                
                # 重置会话
                try:
                    self.db.rollback()
                except Exception:
                    pass
                self.db = SessionLocal()
                
            except Exception as e:
                mcp_logger.error(f"记录工具执行时出现未知错误: {str(e)}")
                return None
        
        return None

    def get_executions(
        self,
        page: int = 1,
        page_size: int = 10,
        tool_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取工具执行记录，支持分页和搜索"""
        try:
            # 确保连接有效
            self._ensure_db_connection()
            
            # 构建查询
            query = self.db.query(ToolExecution)
            
            # 如果有工具名称，添加过滤条件
            if tool_name:
                query = query.filter(ToolExecution.tool_name.ilike(f"%{tool_name}%"))
            
            # 获取总记录数
            total = query.count()
            
            # 获取分页数据
            executions = query.order_by(desc(ToolExecution.created_at))\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "data": [execution.to_dict() for execution in executions]
            }
        except SQLAlchemyError as e:
            mcp_logger.error(f"获取工具执行记录时出错: {str(e)}")
            # 重置会话
            try:
                self.db.rollback()
                self.db = SessionLocal()
            except Exception:
                pass
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "data": []
            }
    
    def get_execution_count(self) -> int:
        """获取工具执行总次数"""
        try:
            # 确保连接有效
            self._ensure_db_connection()
            return self.db.query(func.count(ToolExecution.id)).scalar() or 0
        except SQLAlchemyError:
            # 出错时返回0
            return 0

    def get_last_execution_time(self) -> Optional[str]:
        """获取最近一次工具执行时间"""
        try:
            # 确保连接有效
            self._ensure_db_connection()
            last_execution = self.db.query(ToolExecution)\
                .order_by(desc(ToolExecution.created_at))\
                .first()
            if last_execution:
                return last_execution.created_at.strftime("%Y-%m-%d %H:%M:%S")
            return None
        except SQLAlchemyError:
            return None

# 单例模式
history_service = HistoryService() 