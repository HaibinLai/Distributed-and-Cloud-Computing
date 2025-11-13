import os, grpc, time
from db_pb2 import Empty, ProductId, CreateUserReq, GetUserByNameReq, UpdateUserReq, DeactivateUserReq, PlaceOrderReq, OrderId
from db_pb2_grpc import DbServiceStub
from logging_pb2 import LogEntry
from logging_pb2_grpc import LoggingServiceStub

DB_ADDR = os.getenv("DB_SERVICE_ADDR", "db_service:50051")
LOG_ADDR = os.getenv("LOG_SERVICE_ADDR", "logging_service:50052")

_db_channel = grpc.insecure_channel(DB_ADDR)
_log_channel = grpc.insecure_channel(LOG_ADDR)

db = DbServiceStub(_db_channel)

def log_streamer():
    stub = LoggingServiceStub(_log_channel)
    def generator():
        while True:
            entry = yield  # 由外部 send
            if entry is None: break
            yield entry
    gen = generator()
    next(gen)
    return stub, gen

def make_log(level, message):
    return LogEntry(level=level, message=message, source="api_service", ts_unix_ms=int(time.time()*1000))
