'''
common methods
'''

import argparse


def build_argument_parser(name: str):
    '''
    @param name: name of the test target
    '''
    parser = argparse.ArgumentParser(
        description=f'a kafka producer with {name}'
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
