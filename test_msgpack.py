'''
test kafka producer with orjson
'''
import argparse
import logging
import signal
import sys
from multiprocessing import Event, JoinableQueue, Process
from queue import Empty

from confluent_kafka import KafkaException
from msgspec import MsgspecError, json

from kafka_producer import KafkaProducerService
from logger import log
from structs import PreparedData, Request


def _build_argument_parser():
    parser = argparse.ArgumentParser(
        description='a kafka producer with orjson'
    )

    parser.add_argument(
        '--kafka-bootstrap-server', '-s',
        type=str,
        default='localhost:9092',
        help='a comma-separated list of kafka bootstrap servers (default: "localhost:9092")'
    )

    parser.add_argument(
        '--count', '-c',
        type=int,
        required=True,
        help='number of messages to produce'
    )

    parser.add_argument(
        '--kafka-topic', '-t',
        type=str,
        required=True,
        help='kafka topic for prepared data'
    )

    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='enable debug mode'
    )

    return parser


def build_header(request: Request, extra_headers: dict = None) -> dict:
    '''
    @param prepared_data: a prepared data from Kafka
    @return: headers for feature data
    '''
    return {
        'supplier': request.supplier,
        'fareClass': request.fareClass,
        'timestamp': str(request.timestamp),
        'depDate': request.queries[0].date,
        'retDate': request.queries[1].date,
        **(extra_headers or {})
    }


def _kafka_producer_worker(
    terminate_event: Event,
    kafka_producer_queue: JoinableQueue,
    bootstrap_server: str
) -> None:

    signal.signal(signal.SIGTERM, lambda signum, frame: terminate_event.set())
    signal.signal(signal.SIGINT, lambda signum, frame: terminate_event.set())

    log.info('kafka_producer_worker is started.')
    producer_service = KafkaProducerService(
        bootstrap_server=bootstrap_server,
        topic=args.kafka_topic
    )

    try:
        producer_service.prerequisite_check()
        log.info(
            'producer service prerequisite check passed for kafka bootstrap servers %s',
            bootstrap_server
        )
    except (KafkaException, LookupError, RuntimeError) as err1:
        log.error(err1)
        terminate_event.set()
        return

    encoder = json.Encoder()

    while not terminate_event.is_set():
        try:
            data: PreparedData = kafka_producer_queue.get(timeout=1)
        except Empty:
            log.debug('kafka_producer_queue is empty.')
            continue

        try:
            producer_service.publish(
                key=data.key,
                value=encoder.encode(data),
                headers=build_header(data.request_rt)
            )
        except RuntimeError as error:
            log.error(error)
            continue
        finally:
            kafka_producer_queue.task_done()

    producer_service.close()
    log.info('kafka_producer_worker is terminated.')

    sys.exit(0)

if __name__ == '__main__':

    argument_parser = _build_argument_parser()
    args = argument_parser.parse_args()

    if args.debug:
        log.info('debug mode is enabled')
        log.setLevel(logging.DEBUG)

    _terminate_event = Event()

    _kafka_producer_queue = JoinableQueue(maxsize=10)
    kafka_producer_worker = Process(
        name='KafkaProducerWorker',
        target=_kafka_producer_worker,
        args=(
            _terminate_event,
            _kafka_producer_queue,
            args.kafka_bootstrap_server,
        )
    )
    kafka_producer_worker.start()

    try:
        with open('test_prepared_data.json', 'rb') as f:
            prepared_data = json.decode(f.read(), type=PreparedData)
    except (MsgspecError, FileNotFoundError):
        _terminate_event.set()
        kafka_producer_worker.terminate()
        sys.exit(1)

    COUNT = 0
    try:
        while COUNT < args.count:
            prepared_data.key += str(COUNT)
            COUNT += 1

            _kafka_producer_queue.put(prepared_data)

    finally:
        _terminate_event.set()

    log.info('done.')
    sys.exit(0)
