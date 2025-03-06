"""
软件规划MCP服务器包

这个包提供了软件开发规划工具，帮助用户制定实施计划和管理待办事项。
"""

__version__ = "0.1.0"
__author__ = "MCP开发团队"

from bak.types import Todo, Goal, ImplementationPlan, StorageData
from bak.storage import storage
from bak.prompts import SEQUENTIAL_THINKING_PROMPT, format_plan_as_todos
from bak.server import SoftwarePlanningServer, main 