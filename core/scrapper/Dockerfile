FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common curl gnupg ca-certificates \
    build-essential libssl-dev libffi-dev \
    python3.11 python3.11-venv python3.11-dev python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

WORKDIR /app

COPY core/scrapper/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN crawl4ai-setup

RUN mkdir /app/scrapper


EXPOSE 8001

CMD ["uvicorn", "scrapper.api:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]