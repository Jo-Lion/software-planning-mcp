#!/usr/bin/env python3
"""
软件规划MCP服务器

这个MCP服务器提供了软件开发规划工具，帮助用户制定实施计划和管理待办事项。
"""

import os
import sys
import json
import asyncio
import argparse
from typing import Dict, List, Any, Optional
import time

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import FastMCPError as McpError, ResourceError as ErrorCode

from model_types import Todo, Goal
from storage import storage
from prompts import SEQUENTIAL_THINKING_PROMPT, format_plan_as_todos


class SoftwarePlanningServer:
    """软件规划MCP服务器类"""
    
    def __init__(self):
        """初始化服务器"""
        self.current_goal = None
        self.mcp_server = None
    
    def create_mcp_server(self, server_settings=None):
        """创建并配置MCP服务器实例"""
        # 创建MCP服务器实例
        self.mcp_server = FastMCP("software-planning-tool", **(server_settings or {}))
        
        # 注册资源
        self.mcp_server.resource("planning://current-goal")(self.get_current_goal_resource)
        self.mcp_server.resource("planning://implementation-plan")(self.get_implementation_plan_resource)
        
        # 注册工具
        self.mcp_server.add_tool(self.start_planning_tool, name="start_planning", 
                                description="开始一个新的规划会话，设置目标")
        self.mcp_server.add_tool(self.save_plan_tool, name="save_plan", 
                                description="保存当前实施计划")
        self.mcp_server.add_tool(self.add_todo_tool, name="add_todo", 
                                description="向当前计划添加新的待办事项")
        self.mcp_server.add_tool(self.remove_todo_tool, name="remove_todo", 
                                description="从当前计划中移除待办事项")
        self.mcp_server.add_tool(self.get_todos_tool, name="get_todos", 
                                description="获取当前计划中的所有待办事项")
        self.mcp_server.add_tool(self.update_todo_status_tool, name="update_todo_status", 
                                description="更新待办事项的完成状态")
        
        # 添加健康检查端点
        if hasattr(self.mcp_server, 'app'):
            @self.mcp_server.app.get("/health")
            async def health_check():
                return {"status": "healthy"}
        
        return self.mcp_server
    
    # 资源处理函数
    def get_current_goal_resource(self) -> str:
        """获取当前目标资源"""
        if not self.current_goal:
            raise McpError(
                ErrorCode.InvalidParams,
                "没有活动目标。请先开始一个新的规划会话。"
            )
        
        return json.dumps(self.current_goal.__dict__, ensure_ascii=False, indent=2)
    
    def get_implementation_plan_resource(self) -> str:
        """获取实施计划资源"""
        if not self.current_goal:
            raise McpError(
                ErrorCode.InvalidParams,
                "没有活动目标。请先开始一个新的规划会话。"
            )
        
        plan = asyncio.run(storage.get_plan(self.current_goal.id))
        if not plan:
            raise McpError(
                ErrorCode.InvalidParams,
                "未找到当前目标的实施计划。"
            )
        
        # 将计划转换为可序列化的字典
        plan_dict = {
            "goal_id": plan.goal_id,
            "updated_at": plan.updated_at,
            "todos": [todo.__dict__ for todo in plan.todos]
        }
        
        return json.dumps(plan_dict, ensure_ascii=False, indent=2)
    
    # 工具处理函数
    async def start_planning_tool(self, goal: str) -> str:
        """开始一个新的规划会话，设置目标"""
        self.current_goal = await storage.create_goal(goal)
        await storage.create_plan(self.current_goal.id)
        
        return SEQUENTIAL_THINKING_PROMPT
    
    async def save_plan_tool(self, plan: str) -> str:
        """保存当前实施计划"""
        if not self.current_goal:
            raise McpError(
                ErrorCode.InvalidRequest,
                "没有活动目标。请先开始一个新的规划会话。"
            )
        
        todos = format_plan_as_todos(plan)
        
        # 添加待办事项
        added_count = 0
        for todo_data in todos:
            await storage.add_todo(self.current_goal.id, todo_data)
            added_count += 1
        
        return f"成功将 {added_count} 个待办事项保存到实施计划中。"
    
    async def add_todo_tool(self, title: str, description: str, complexity: int, code_example: Optional[str] = None) -> str:
        """向当前计划添加新的待办事项"""
        if not self.current_goal:
            raise McpError(
                ErrorCode.InvalidRequest,
                "没有活动目标。请先开始一个新的规划会话。"
            )
        
        todo_data = {
            "title": title,
            "description": description,
            "complexity": complexity,
            "code_example": code_example
        }
        
        new_todo = await storage.add_todo(self.current_goal.id, todo_data)
        
        return json.dumps(new_todo.__dict__, ensure_ascii=False, indent=2)
    
    async def remove_todo_tool(self, todo_id: str) -> str:
        """从当前计划中移除待办事项"""
        if not self.current_goal:
            raise McpError(
                ErrorCode.InvalidRequest,
                "没有活动目标。请先开始一个新的规划会话。"
            )
        
        await storage.remove_todo(self.current_goal.id, todo_id)
        
        return f"成功移除待办事项 {todo_id}"
    
    async def get_todos_tool(self) -> str:
        """获取当前计划中的所有待办事项"""
        if not self.current_goal:
            raise McpError(
                ErrorCode.InvalidRequest,
                "没有活动目标。请先开始一个新的规划会话。"
            )
        
        todos = await storage.get_todos(self.current_goal.id)
        
        # 将待办事项列表转换为可序列化的字典列表
        todos_list = [todo.__dict__ for todo in todos]
        
        return json.dumps(todos_list, ensure_ascii=False, indent=2)
    
    async def update_todo_status_tool(self, todo_id: Any, is_complete: bool) -> str:
        """更新待办事项的完成状态"""
        if not self.current_goal:
            raise McpError(
                ErrorCode.InvalidRequest,
                "没有活动目标。请先开始一个新的规划会话。"
            )
        
        # 确保todo_id是字符串类型
        todo_id_str = str(todo_id)
        
        updated_todo = await storage.update_todo_status(self.current_goal.id, todo_id_str, is_complete)
        
        return json.dumps(updated_todo.__dict__, ensure_ascii=False, indent=2)
    
    def run(self, transport: str = "stdio", host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """运行MCP服务器"""
        # 初始化存储
        asyncio.run(storage.initialize())
        
        # 设置服务器配置
        server_settings = {}
        if transport == "sse":
            server_settings = {
                "host": host,
                "port": port,
                "debug": debug,
                "log_level": "DEBUG" if debug else "INFO"
            }
        
        # 创建并配置MCP服务器
        self.create_mcp_server(server_settings)
        
        # 启动服务器
        if transport == "sse":
            print(f"启动SSE服务器，监听地址: {host}:{port}...")
            # 添加一个短暂的延迟，确保服务器初始化完成
            time.sleep(1)
            self.mcp_server.run(transport="sse")
        else:
            print("启动stdio服务器...")
            self.mcp_server.run(transport="stdio")


def main():
    """主函数，解析命令行参数并启动服务器"""
    # 从环境变量获取默认值
    default_port = int(os.environ.get("SOFTWARE_PLANNING_PORT", "8000"))
    default_host = os.environ.get("SOFTWARE_PLANNING_HOST", "0.0.0.0")
    default_transport = os.environ.get("SOFTWARE_PLANNING_TRANSPORT", "sse")
    default_debug = os.environ.get("SOFTWARE_PLANNING_DEBUG", "").lower() in ("true", "1", "yes")
    
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description="软件规划MCP服务器")
    parser.add_argument("--transport", type=str, default=default_transport, choices=["stdio", "sse"], 
                        help=f"传输类型: stdio 或 sse (默认: {default_transport})")
    parser.add_argument("--debug", action="store_true", default=default_debug,
                        help="启用调试模式")
    parser.add_argument("--port", type=int, default=default_port,
                        help=f"SSE服务器端口号 (默认: {default_port})")
    parser.add_argument("--host", type=str, default=default_host,
                        help=f"SSE服务器主机地址 (默认: {default_host})")
    parser.add_argument("--init-delay", type=float, default=2.0,
                        help="服务器初始化延迟时间（秒）(默认: 2.0)")
    
    args = parser.parse_args()
    
    # 设置调试模式
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # 创建服务器实例
    server = SoftwarePlanningServer()
    
    # 运行服务器
    try:
        # 如果是SSE模式，添加一个短暂的延迟
        if args.transport == "sse" and args.init_delay > 0:
            print(f"等待 {args.init_delay} 秒以确保服务器初始化完成...")
            time.sleep(args.init_delay)
            
        # 直接调用run方法，不使用asyncio.run
        server.run(
            transport=args.transport,
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 