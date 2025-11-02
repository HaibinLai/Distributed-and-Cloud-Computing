import os, grpc
from concurrent.futures import ThreadPoolExecutor
from confluent_kafka import Producer
import logging_pb2, logging_pb2_grpc

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "api-logs")

producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP})

class LoggingImpl(logging_pb2_grpc.LoggingServiceServicer):
    def StreamLogs(self, request_iterator, context):
        count = 0
        for entry in request_iterator:
            producer.produce(KAFKA_TOPIC, key=entry.level, value=f"{entry.ts_unix_ms}|{entry.source}|{entry.message}")
            count += 1
        producer.flush()
        return logging_pb2.LogAck(count=count)

def serve():
    s = grpc.server(ThreadPoolExecutor(max_workers=8))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingImpl(), s)
    s.add_insecure_port("[::]:50052")
    s.start(); s.wait_for_termination()

if __name__ == "__main__":
    serve()
