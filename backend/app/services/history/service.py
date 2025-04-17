from typing import List, Dict, Any, Optional
import json
from sqlalchemy import desc, func

from app.models.engine import engine
from app.models.activities.activity import Activity
from app.models.tools.tool_execution import ToolExecution
from sqlalchemy.orm import sessionmaker

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class HistoryService:
    """工具调用历史记录服务"""

    def __init__(self):
        """初始化数据库会话"""
        self.db = SessionLocal()

    def __del__(self):
        """关闭数据库会话"""
        self.db.close()

    def record_tool_execution(
        self, 
        tool_name: str, 
        description: str, 
        parameters: Dict[str, Any], 
        result: Any, 
        status: str, 
        execution_time: int
    ) -> ToolExecution:
        """记录工具执行"""
        db_record = ToolExecution(
            tool_name=tool_name,
            description=description,
            parameters=json.dumps(parameters),
            result=json.dumps(result) if result is not None else None,
            status=status,
            execution_time=execution_time
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)

        # 添加活动记录
        # activity_content = f"执行工具：{tool_name}"
        # self.add_activity(activity_content, "tool_execution", db_record.id)

        return db_record

    def get_executions(
        self,
        page: int = 1,
        page_size: int = 10,
        tool_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取工具执行记录，支持分页和搜索
        
        Args:
            page: 页码，从1开始
            page_size: 每页记录数
            tool_name: 工具名称，用于搜索过滤
            
        Returns:
            包含分页信息和数据的字典
        """
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
    
    def get_execution_count(self) -> int:
        """获取工具执行总次数"""
        return self.db.query(func.count(ToolExecution.id)).scalar()

    def get_last_execution_time(self) -> Optional[str]:
        """获取最近一次工具执行时间"""
        last_execution = self.db.query(ToolExecution)\
            .order_by(desc(ToolExecution.created_at))\
            .first()
        if last_execution:
            return last_execution.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def add_activity(
        self, 
        content: str, 
        activity_type: str, 
        related_id: Optional[int] = None
    ) -> Activity:
        """添加活动记录"""
        db_activity = Activity(
            content=content,
            activity_type=activity_type,
            related_id=related_id
        )
        self.db.add(db_activity)
        self.db.commit()
        self.db.refresh(db_activity)
        return db_activity

    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的活动记录"""
        activities = self.db.query(Activity)\
            .order_by(desc(Activity.created_at))\
            .limit(limit)\
            .all()
        return [activity.to_dict() for activity in activities]


# 单例模式
history_service = HistoryService() 