# src/logging_service/Dockerfile

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 安装编译依赖和 librdkafka（给 confluent-kafka 用）
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir grpcio grpcio-tools confluent-kafka

# 拷贝服务代码
COPY . /app

EXPOSE 50052

CMD ["python", "server.py"]

# docker-compose down    # 把旧容器全关掉
# docker-compose up --build -d