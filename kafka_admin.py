'''
Kafka Admin
'''

import time
from confluent_kafka.admin import AdminClient, NewTopic

from logger import log


class KafkaAdminService:
    '''
    admin
    '''

    def __init__(self, bootstrap_server: str) -> None:
        self.__admin = AdminClient({
            'bootstrap.servers': bootstrap_server
        })

    def create_topic(self, topic: str, partitions: int = 4, recreate: bool = True) -> None:
        '''
        create topic
        '''

        if topic in self.__admin.list_topics().topics:
            log.info("Topic '%s' already exists.", topic)
            if recreate:
                log.info("Recreating topic '%s'...", topic)
                self.__admin.delete_topics([topic])

                count = 5
                while count > 0:
                    if topic not in self.__admin.list_topics().topics:
                        break
                    log.info("Waiting for topic '%s' to be deleted...", topic)
                    count -= 1
                    time.sleep(1)
            else:
                return

        new_topic = NewTopic(topic, partitions, config={
            'compression.type': 'lz4',
            'retention.bytes': '1000000000'  # 1GB per partition
        })
        self.__admin.create_topics([new_topic])

        count = 5
        while count > 0:
            if topic in self.__admin.list_topics().topics:
                break
            log.info("Waiting for topic '%s' to be created...", topic)
            count -= 1
            time.sleep(1)

        log.info("Topic '%s' created.", topic)
