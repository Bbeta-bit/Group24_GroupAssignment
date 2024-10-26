# 使用官方 Python 基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev

# 复制并安装 Python 依赖
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 复制代码并运行
COPY . .
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:8080"]
