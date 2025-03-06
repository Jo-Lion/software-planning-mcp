"""
软件规划MCP服务器的数据存储模块
"""

import os
import json
import time
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple, Union
from pathlib import Path

from bak.types import Todo, Goal, ImplementationPlan, StorageData


class Storage:
    """数据存储类，负责管理软件规划数据的持久化"""
    
    def __init__(self):
        # 在用户主目录下创建存储目录
        self.storage_dir = Path.home() / '.software-planning-tool'
        self.storage_path = self.storage_dir / 'data.json'
        self.data = StorageData(goals={}, plans={})
    
    async def initialize(self) -> None:
        """初始化存储，读取现有数据或创建新的存储文件"""
        try:
            # 确保存储目录存在
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            
            # 尝试读取现有数据
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 将JSON数据转换为对象
                goals = {}
                for goal_id, goal_data in data.get('goals', {}).items():
                    goals[goal_id] = Goal(
                        id=goal_data['id'],
                        description=goal_data['description'],
                        created_at=goal_data['created_at']
                    )
                
                plans = {}
                for plan_id, plan_data in data.get('plans', {}).items():
                    todos = []
                    for todo_data in plan_data.get('todos', []):
                        todos.append(Todo(
                            id=todo_data['id'],
                            title=todo_data['title'],
                            description=todo_data['description'],
                            complexity=todo_data['complexity'],
                            code_example=todo_data.get('code_example'),
                            is_complete=todo_data['is_complete'],
                            created_at=todo_data['created_at'],
                            updated_at=todo_data['updated_at']
                        ))
                    
                    plans[plan_id] = ImplementationPlan(
                        goal_id=plan_data['goal_id'],
                        todos=todos,
                        updated_at=plan_data['updated_at']
                    )
                
                self.data = StorageData(goals=goals, plans=plans)
            else:
                # 如果文件不存在，使用默认空数据
                await self._save()
        except Exception as e:
            print(f"初始化存储时出错: {e}")
            # 使用默认空数据
            self.data = StorageData(goals={}, plans={})
            await self._save()
    
    async def _save(self) -> None:
        """保存数据到存储文件"""
        try:
            # 将对象转换为可序列化的字典
            data_dict = {
                'goals': {},
                'plans': {}
            }
            
            for goal_id, goal in self.data.goals.items():
                data_dict['goals'][goal_id] = {
                    'id': goal.id,
                    'description': goal.description,
                    'created_at': goal.created_at
                }
            
            for plan_id, plan in self.data.plans.items():
                todos_list = []
                for todo in plan.todos:
                    todos_list.append({
                        'id': todo.id,
                        'title': todo.title,
                        'description': todo.description,
                        'complexity': todo.complexity,
                        'code_example': todo.code_example,
                        'is_complete': todo.is_complete,
                        'created_at': todo.created_at,
                        'updated_at': todo.updated_at
                    })
                
                data_dict['plans'][plan_id] = {
                    'goal_id': plan.goal_id,
                    'todos': todos_list,
                    'updated_at': plan.updated_at
                }
            
            # 写入文件
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存数据时出错: {e}")
    
    async def create_goal(self, description: str) -> Goal:
        """创建新的目标"""
        goal_id = str(int(time.time() * 1000))  # 使用时间戳作为ID
        now = datetime.now().isoformat()
        
        goal = Goal(
            id=goal_id,
            description=description,
            created_at=now
        )
        
        self.data.goals[goal_id] = goal
        await self._save()
        return goal
    
    async def get_goal(self, goal_id: str) -> Optional[Goal]:
        """获取指定ID的目标"""
        return self.data.goals.get(goal_id)
    
    async def create_plan(self, goal_id: str) -> ImplementationPlan:
        """为指定目标创建实现计划"""
        now = datetime.now().isoformat()
        
        plan = ImplementationPlan(
            goal_id=goal_id,
            todos=[],
            updated_at=now
        )
        
        self.data.plans[goal_id] = plan
        await self._save()
        return plan
    
    async def get_plan(self, goal_id: str) -> Optional[ImplementationPlan]:
        """获取指定目标的实现计划"""
        return self.data.plans.get(goal_id)
    
    async def add_todo(self, goal_id: str, todo_data: Dict[str, Any]) -> Todo:
        """向实现计划添加待办事项"""
        plan = await self.get_plan(goal_id)
        if not plan:
            raise ValueError(f"未找到目标 {goal_id} 的实现计划")
        
        todo_id = str(int(time.time() * 1000))  # 使用时间戳作为ID
        now = datetime.now().isoformat()
        
        todo = Todo(
            id=todo_id,
            title=todo_data['title'],
            description=todo_data['description'],
            complexity=todo_data['complexity'],
            code_example=todo_data.get('code_example'),
            is_complete=False,
            created_at=now,
            updated_at=now
        )
        
        plan.todos.append(todo)
        plan.updated_at = now
        await self._save()
        return todo
    
    async def remove_todo(self, goal_id: str, todo_id: str) -> None:
        """从实现计划中移除待办事项"""
        plan = await self.get_plan(goal_id)
        if not plan:
            raise ValueError(f"未找到目标 {goal_id} 的实现计划")
        
        # 查找待办事项
        for i, todo in enumerate(plan.todos):
            if todo.id == todo_id:
                # 移除待办事项
                plan.todos.pop(i)
                plan.updated_at = datetime.now().isoformat()
                await self._save()
                return
        
        raise ValueError(f"未找到ID为 {todo_id} 的待办事项")
    
    async def update_todo_status(self, goal_id: str, todo_id: str, is_complete: bool) -> Todo:
        """更新待办事项的完成状态"""
        plan = await self.get_plan(goal_id)
        if not plan:
            raise ValueError(f"未找到目标 {goal_id} 的实现计划")
        
        # 查找待办事项
        for todo in plan.todos:
            if todo.id == todo_id:
                # 更新状态
                todo.is_complete = is_complete
                todo.updated_at = datetime.now().isoformat()
                plan.updated_at = todo.updated_at
                await self._save()
                return todo
        
        raise ValueError(f"未找到ID为 {todo_id} 的待办事项")
    
    async def get_todos(self, goal_id: str) -> List[Todo]:
        """获取指定目标的所有待办事项"""
        plan = await self.get_plan(goal_id)
        if not plan:
            raise ValueError(f"未找到目标 {goal_id} 的实现计划")
        
        return plan.todos


# 创建全局存储实例
storage = Storage() 