"""
软件规划MCP服务器的数据类型定义
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Todo:
    """待办事项数据类型"""
    id: str
    title: str
    description: str
    complexity: int
    code_example: Optional[str] = None
    is_complete: bool = False
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Goal:
    """目标数据类型"""
    id: str
    description: str
    created_at: str


@dataclass
class ImplementationPlan:
    """实现计划数据类型"""
    goal_id: str
    todos: List[Todo]
    updated_at: str


@dataclass
class StorageData:
    """存储数据类型"""
    goals: Dict[str, Goal]
    plans: Dict[str, ImplementationPlan] 