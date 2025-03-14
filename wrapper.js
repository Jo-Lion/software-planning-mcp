#!/usr/bin/env node
const { spawn } = require('child_process');

// 启动Python服务器
console.log('Starting Python MCP server with STDIO transport...');

// 创建子进程运行Python服务器
const pythonProcess = spawn('python', ['server.py', '--transport', 'stdio'], {
  stdio: ['pipe', process.stdout, process.stderr]
});

// 处理Python进程的输入/输出
process.stdin.pipe(pythonProcess.stdin);

// 处理退出信号
process.on('SIGINT', () => {
  pythonProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
  pythonProcess.kill('SIGTERM');
});

// 处理Python进程退出
pythonProcess.on('exit', (code) => {
  console.log(`Python process exited with code ${code}`);
  process.exit(code);
}); 