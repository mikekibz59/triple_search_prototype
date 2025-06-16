# 1. lightweight Python base
FROM python:3.12-slim

# 2. set workdir
WORKDIR /app

# 3. install deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 4. copy the code
RUN mkdir /app/on_demand_prototype

EXPOSE 8000

# 6. run the API
CMD ["uvicorn", "on_demand_prototype.api:app", "--host", "0.0.0.0", "--port", "8003"]