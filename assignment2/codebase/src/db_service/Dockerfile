FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖：psycopg2 需要 libpq-dev，gRPC 需要 build-essential
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 把 requirements.txt 放进来
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip3 install --no-cache-dir   requests  PyJWT 

# 拷贝代码
COPY . .

# 运行 gRPC 服务器
CMD ["python", "server.py"]
