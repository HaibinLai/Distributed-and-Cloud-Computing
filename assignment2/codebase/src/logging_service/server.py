import json
import logging
from concurrent import futures

import grpc
import logging_pb2
import logging_pb2_grpc

from local_publisher import LocalKafkaPublisher

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

KAFKA_TOPIC = "api-logs"


class LoggingService(logging_pb2_grpc.LoggingServiceServicer):
    def __init__(self, publisher):
        self.publisher = publisher

    def StreamLogs(self, request_iterator, context):
        count = 0
        for req in request_iterator:
            payload = {
                "service_name": req.service_name,
                "level": req.level,
                "path": req.path,
                "method": req.method,
                "user_sid": req.user_sid,
                "message": req.message,
                "timestamp_ms": req.timestamp_ms
            }
            try:
                self.publisher.publish(
                    topic=KAFKA_TOPIC,
                    key=req.service_name.encode(),
                    value=json.dumps(payload).encode()
                )
                count += 1
            except Exception as e:
                LOGGER.error("Publish fail: %s", e)

        LOGGER.info("Received %d logs", count)
        return logging_pb2.LogSummary(count=count)


def serve():
    publisher = LocalKafkaPublisher("kafka:9092")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(
        LoggingService(publisher), server
    )

    server.add_insecure_port("[::]:50052")
    LOGGER.info("Logging Service running at :50052")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
