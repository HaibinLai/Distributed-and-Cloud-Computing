# import time
# from datetime import datetime

# from confluent_kafka import Producer

# '''
# Kafka Producer: https://docs.confluent.io/kafka-clients/python/current/overview.html#ak-producer
# Kafka Consumer: https://kafka.apache.org/quickstart#quickstart_consume
# '''

# # connect to redis database #0
# producer = Producer({'bootstrap.servers': 'localhost:9093'})
# topic = 'log-channel'

# # produce messages
# # try:
# #   while True:
# #     msg = f'Hello at time = {datetime.now()}'
# #     producer.produce(topic, msg.encode('utf-8'))
# #     producer.flush()
# #     print(msg)
# #     time.sleep(1)
# # except KeyboardInterrupt:
# #   print('\nStopped by keyboard interrupt')
# # finally:
# #   producer.flush()

# # local_publisher.py （结构示意）
# from confluent_kafka import Producer
# import os

# class LocalKafkaPublisher:
#     def __init__(self, bootstrap_servers: str):

#         bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

#         self.producer = Producer({
#             "bootstrap.servers": bootstrap,
#         })


#     def publish(self, topic: str, key: bytes, value: bytes):
#         self.producer.produce(topic=topic, key=key, value=value)
#         # 简单场景可以直接 flush，或者定期 flush
#         self.producer.flush()

from confluent_kafka import Producer


class LocalKafkaPublisher:
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def publish(self, topic: str, key: bytes, value: bytes):
        self.producer.produce(topic=topic, key=key, value=value)
        self.producer.flush()
