FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 注意：实际的启动命令将由smithery.yaml中的commandFunction定义
# 这里的CMD是为了在非Smithery环境中使用
CMD ["python", "server.py", "--transport", "stdio"] 