'''
Kafka Producer
'''
from datetime import datetime

from confluent_kafka import KafkaException, Producer
from confluent_kafka.admin import ClusterMetadata

from logger import log


class KafkaProducerService:
    '''
    main class
    '''

    def __init__(self, bootstrap_server: str, topic: str) -> None:
        self.__producer = Producer({
            'bootstrap.servers': bootstrap_server
        })

        self.__topic = topic
        self.__count = 0
        self.__previous_count_timestamp = datetime.now().timestamp()

    def prerequisite_check(self) -> None:
        '''
        prerequisite check
        '''
        cluster_meta_data: ClusterMetadata = self.__producer.list_topics(
            timeout=5)
        if self.__topic not in cluster_meta_data.topics:
            raise LookupError(
                f"The topic '{self.__topic}' does not exist in Kafka. Create the topic first."
            )

    def close(self) -> None:
        '''
        close producer
        '''
        self.__producer.flush()

    def publish(self, key: str, value: bytes, headers: dict) -> None:
        '''
        publish message
        '''
        try:
            self.__producer.produce(
                self.__topic,
                key=key,
                value=value,
                headers=headers
            )
        except BufferError as error:
            raise RuntimeError(
                "internal producer message queue is full"
            ) from error
        except KafkaException as error:
            raise RuntimeError(
                "error adding to producer message queue"
            ) from error

        num_messages_to_be_delievered = len(self.__producer)
        if num_messages_to_be_delievered > 1000:
            log.debug("wait for %s messages to be delivered to Kafka...",
                      num_messages_to_be_delievered)
            try:
                num_message = self.__producer.flush()
            except KafkaException as error:
                raise RuntimeError(
                    "error when flushing producer message queue to Kafka"
                ) from error

            log.debug("%d messages still in Kafka", num_message)

        self.__count += 1
        self.__count_published()

    def __count_published(self) -> None:
        current_count_timestamp = datetime.now().timestamp()
        if current_count_timestamp - self.__previous_count_timestamp >= 1:
            self.__previous_count_timestamp = current_count_timestamp

            if self.__count == 0:
                return

            log.info("%d messages published (%s messages pending for delivery)",
                     self.__count, len(self.__producer))
            self.__count = 0
