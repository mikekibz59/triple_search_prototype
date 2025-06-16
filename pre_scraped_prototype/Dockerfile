FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1
WORKDIR /app

# Copy from the build context root
COPY ./pre_scraped_prototype/requirements.txt .
RUN pip install -r requirements.txt

# Copy the entire pre_scraped_prototype directory
COPY ./pre_scraped_prototype/ .

# Build the SQLite DB
RUN python ingest_sqlite.py

EXPOSE 8002
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8002"]