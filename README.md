# Kafka with `orjson` vs `msgspec`

This project is to help profiling memory usage of the [Kafka](https://kafka.apache.org/) with two different serialization libraries:

- `orjson`
- `msgspec`

## Usage

```bash
python test_<serializer>.py [-h] [--kafka-bootstrap-server KAFKA_BOOTSTRAP_SERVER] --count COUNT --kafka-topic KAFKA_TOPIC
```

## Setup

### Python Virutal Environment

```bash
virtualenv ./venv # or python3 -m venv venv

. venv/bin/activate

pip install -r requirements.txt
```

### Kafka

```bash
docker run -d --name zookeeper --network host zookeeper:latest

docker run -d --name=kafka --network host -e KAFKA_ZOOKEEPER_CONNECT=localhost:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 confluentinc/cp-kafka:latest
```

## Run

```bash
PYTHONMALLOC=malloc memray run --follow-fork test_orjson.py -s localhost:9092 -t test -c 99999

PYTHONMALLOC=malloc memray run --follow-fork test_msgspec.py -s localhost:9092 -t test -c 99999
```

## Results

Find the result files starting with `memray-` in the current directory.

```bash
memray table --leaks <result file>
```

Then open the generated HTML report in your browser.
