# 软件规划MCP服务器
https://github.com/NightTrek/Software-planning-mcp 项目python版，方便使用sse接入cursor
这个MCP服务器提供了软件开发规划工具，帮助用户制定实施计划和管理待办事项。

## 功能特点

- 创建软件开发目标
- 制定详细的实施计划
- 管理待办事项列表
- 跟踪任务完成状态
- 提供结构化的思考过程

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/software-planning-mcp.git
cd software-planning-mcp

# 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
```

## 使用方法

### 启动服务器

```bash
# 使用SSE传输协议（推荐用于Cursor集成）
software-planning-mcp --debug

# 使用自定义端口
software-planning-mcp --port 9000 --debug

# 使用自定义主机地址
software-planning-mcp --host 127.0.0.1 --debug

# 使用stdio传输协议（用于命令行测试）
software-planning-mcp --transport stdio --debug
```

### 在Cursor中配置MCP服务器

1. 打开Cursor编辑器
2. 进入设置 -> MCP Servers
3. 点击"Add new MCP server"
4. 输入服务器链接：`http://localhost:8000/sse`（如果使用了自定义端口，请相应修改）
5. 保存配置

## 可用工具

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| start_planning | 开始一个新的规划会话，设置目标 | goal: 软件开发目标 |
| save_plan | 保存当前实施计划 | plan: 实施计划文本 |
| add_todo | 向当前计划添加新的待办事项 | title: 标题<br>description: 描述<br>complexity: 复杂度(0-10)<br>code_example: 代码示例(可选) |
| remove_todo | 从当前计划中移除待办事项 | todo_id: 待办事项ID |
| get_todos | 获取当前计划中的所有待办事项 | 无 |
| update_todo_status | 更新待办事项的完成状态 | todo_id: 待办事项ID<br>is_complete: 完成状态 |

## 可用资源

| 资源URI | 描述 |
|---------|------|
| planning://current-goal | 当前软件开发目标 |
| planning://implementation-plan | 当前实施计划及待办事项 |

## 环境变量

- `SOFTWARE_PLANNING_PORT`: 设置SSE服务器端口号（默认：8000）
- `SOFTWARE_PLANNING_HOST`: 设置SSE服务器主机地址（默认：0.0.0.0）
- `SOFTWARE_PLANNING_TRANSPORT`: 设置传输类型，可选值为"stdio"或"sse"（默认："sse"）
- `SOFTWARE_PLANNING_DEBUG`: 启用调试模式，可选值为"true"、"1"或"yes"（默认：禁用）

## 许可证

MIT 