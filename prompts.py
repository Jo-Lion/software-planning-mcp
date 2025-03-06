"""
软件规划MCP服务器的提示模板模块
"""

import re
from typing import List, Dict, Any


# 顺序思考提示模板
SEQUENTIAL_THINKING_PROMPT = """您是一位高级软件架构师，通过基于问题的顺序思考过程指导软件功能的开发。您的角色是：

1. 理解目标
- 首先彻底理解提供的目标
- 将复杂需求分解为可管理的组件
- 识别潜在的挑战和约束

2. 提出战略性问题
提出关于以下方面的问题：
- 系统架构和设计模式
- 技术要求和约束
- 与现有系统的集成点
- 安全考虑
- 性能要求
- 可扩展性需求
- 数据管理和存储
- 用户体验要求
- 测试策略
- 部署考虑

3. 分析回答
- 处理用户回答以完善理解
- 识别信息中的差距
- 发现潜在风险或挑战
- 考虑替代方法
- 验证假设

4. 制定计划
随着理解的深入：
- 创建详细、可操作的实施步骤
- 为每个任务包含复杂度评分（0-10）
- 在有帮助的地方提供代码示例
- 考虑任务之间的依赖关系
- 将大任务分解为更小的子任务
- 包含测试和验证步骤
- 记录架构决策

5. 迭代和完善
- 继续提问直到所有方面都清晰
- 根据新信息完善计划
- 调整任务分解和复杂度评分
- 随着细节的出现添加实施细节

6. 完成
该过程将持续进行，直到用户表示对计划满意为止。最终计划应该是：
- 全面且可操作
- 结构良好且有优先级
- 技术要求明确
- 实施细节具体
- 复杂度评估现实

指南：
- 一次提出一个重点问题
- 保持来自先前回答的上下文
- 在问题中具体且技术性
- 考虑即时和长期影响
- 记录关键决策及其理由
- 在任务描述中包含相关代码示例
- 考虑安全性、性能和可维护性
- 专注于实用、可实施的解决方案

首先分析提供的目标并提出您的第一个战略问题。"""


def format_plan_as_todos(plan: str) -> List[Dict[str, Any]]:
    """
    将计划文本格式化为待办事项列表
    
    这是一个简化的实现，在实际系统中，可能需要更复杂的解析逻辑
    来从计划文本中提取待办事项
    """
    todos = []
    
    # 按空行分割部分
    sections = [s.strip() for s in plan.split('\n\n') if s.strip()]
    
    for section in sections:
        lines = section.split('\n')
        
        # 提取标题（第一行，去除可能的编号）
        title = re.sub(r'^[0-9]+\.\s*', '', lines[0]).strip()
        
        # 提取复杂度
        complexity_match = re.search(r'复杂度:\s*([0-9]+)', section) or re.search(r'Complexity:\s*([0-9]+)', section)
        complexity = int(complexity_match.group(1)) if complexity_match else 5
        
        # 提取代码示例（如果有）
        code_example_match = re.search(r'```(.*?)```', section, re.DOTALL)
        code_example = code_example_match.group(1).strip() if code_example_match else None
        
        # 提取描述（去除标题、复杂度和代码示例）
        description = section
        description = re.sub(r'^[0-9]+\.\s*[^\n]*\n', '', description)  # 移除标题行
        description = re.sub(r'复杂度:\s*[0-9]+', '', description)  # 移除复杂度
        description = re.sub(r'Complexity:\s*[0-9]+', '', description)  # 移除英文复杂度
        description = re.sub(r'```.*?```', '', description, flags=re.DOTALL)  # 移除代码示例
        description = description.strip()
        
        todos.append({
            'title': title,
            'description': description,
            'complexity': complexity,
            'code_example': code_example
        })
    
    return todos 