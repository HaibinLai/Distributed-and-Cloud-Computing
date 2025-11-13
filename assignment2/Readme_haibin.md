
```
SUSTech_Merch_Store/
├── api_service/                 # 工程1: RESTful API服务
│   ├── openapi.yaml
├── db_service/                  # 工程2: 数据库gRPC服务
│   ├── local_manager.py
│   ├── requirements.txt
├── logging_service/             # 工程3: 日志gRPC服务
│   ├── local_publisher
│   ├── requirements.txt
├── docker-compose.yml          # Docker编排配置
├── .env                        # 环境变量
└── init.sql                    # 数据库初始化脚本
```


```
┌─────────────────────────────┐
│       前端 / 客户端         │
│   (用户浏览器 / curl / app) │
└──────────────┬──────────────┘
               │  RESTful HTTP (JSON)
               ▼
┌─────────────────────────────┐
│        API Service          │
│ FastAPI + JWT + OpenAPI     │
│ 负责：HTTP接口、登录鉴权     │
└──────────────┬──────────────┘
               │  gRPC（二进制通信）
               ▼
┌─────────────────────────────┐
│  后端内部服务（gRPC层）     │
│  • DB Service：访问数据库   │
│  • Logging Service：写日志  │
└──────────────┬──────────────┘
               │  SQL / Kafka
               ▼
┌─────────────────────────────┐
│   PostgreSQL + Kafka 等基础设施 │
└─────────────────────────────┘
```


🔁 总体执行流程（从请求到数据库）

用户浏览器发请求：

POST /orders { "product_id": 1, "quantity": 2 }


FastAPI（API Service）收到请求 → 验证 JWT。

API Service 用 DbServiceStub 调用 gRPC：

db.PlaceOrder(PlaceOrderReq(user_id=123, product_id=1, quantity=2))


DB Service 收到请求 → 扣库存 → 写数据库 → 返回结果。

API Service 收到 gRPC 返回 → 转成 JSON → 回复给浏览器。

同时 API Service 把日志写入 Logging Service → Logging Service 发往 Kafka。


```
PYTHONPATH=src uvicorn openapi_server.main:app --host 0.0.0.0
```