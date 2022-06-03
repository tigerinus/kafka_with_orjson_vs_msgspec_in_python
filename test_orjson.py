'''
test kafka producer with orjson
'''
import logging
import signal
import sys
from multiprocessing import Event, JoinableQueue, Process
from queue import Empty

from confluent_kafka import KafkaException
import orjson as json

from kafka_producer import KafkaProducerService
from logger import log
from common import build_argument_parser


def build_header(request: dict, extra_headers: dict = None) -> dict:
    '''
    @param prepared_data: a prepared data from Kafka
    @return: headers for feature data
    '''
    return {
        'supplier': request["supplier"],
        'fareClass': request["fareClass"],
        'timestamp': str(request["timestamp"]),
        'depDate': request["queries"][0]["date"],
        'retDate': request["queries"][1]["date"],
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

    while not terminate_event.is_set():
        try:
            data: dict = kafka_producer_queue.get(timeout=1)
        except Empty:
            log.debug('kafka_producer_queue is empty.')
            continue

        try:
            producer_service.publish(
                key=data["key"],
                value=json.dumps(data), # pylint: disable=no-member
                headers=build_header(data["request_rt"])
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

    argument_parser = build_argument_parser('orjson')
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
            prepared_data = json.loads(f.read())
    except (json.JSONDecodeError, FileNotFoundError):
        _terminate_event.set()
        kafka_producer_worker.terminate()
        sys.exit(1)

    COUNT = 0
    try:
        while COUNT < args.count:
            prepared_data["key"] += str(COUNT)
            COUNT += 1

            _kafka_producer_queue.put(prepared_data)

    finally:
        _terminate_event.set()

    log.info('done.')
    sys.exit(0)
