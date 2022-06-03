FROM python:3-slim AS buildtime

WORKDIR /app

RUN apt-get update
RUN apt-get --yes dist-upgrade
RUN apt-get --no-install-recommends --yes install gcc libc6-dev librdkafka-dev

RUN python -m venv venv

ENV PATH="./venv/bin:$PATH" 
RUN --mount=type=cache,id=cache-pip,target=/root/.cache/pip pip install --upgrade pip

COPY requirements.txt .
RUN --mount=type=cache,id=cache-pip,target=/root/.cache/pip pip install -v -r requirements.txt

COPY *.py src/
COPY *.json src/

FROM python:3-slim AS runtime

WORKDIR /app

RUN apt-get update
RUN apt-get --yes dist-upgrade
RUN apt-get --no-install-recommends --yes install librdkafka1 procps curl

COPY --from=buildtime /app/venv venv
COPY --from=buildtime /app/src .

ENV PATH="./venv/bin:$PATH"

CMD tail -f /dev/null
