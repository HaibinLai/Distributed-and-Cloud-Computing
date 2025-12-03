import time
import grpc

# import logging_pb2
# import logging_pb2_grpc

from openapi_server import logging_pb2_grpc, logging_pb2
import os


LOGGING_ADDR = os.getenv("LOGGING_ADDR", "logging_service:50052")

_channel = None
_stub = None


def get_logging_stub():
    global _channel, _stub
    if _stub is None:
        _channel = grpc.insecure_channel(LOGGING_ADDR)
        _stub = logging_pb2_grpc.LoggingServiceStub(_channel)
    return _stub


def send_logs(logs):
    """
    logs: List[dict]，例如：
      {
        "service_name": "api-service",
        "level": "INFO",
        "path": "/users/login",
        "method": "POST",
        "user_sid": "123",
        "message": "login ok"
      }
    """
    stub = get_logging_stub()

    INSTANCE_NAME = os.getenv("INSTANCE_NAME", "unknown")

    def gen():
        for log in logs:
            yield logging_pb2.LogMessage(
                service_name=INSTANCE_NAME,
                level=log.get("level", "INFO"),
                path=log.get("path", ""),
                method=log.get("method", ""),
                user_sid=log.get("user_sid", ""),
                message=log.get("message", ""),
                timestamp_ms=int(time.time() * 1000)
            )

    return stub.StreamLogs(gen())
