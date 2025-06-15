# ──────────────────────────────────────────────────────────────
# FastAPI Search Service
# Base: tiangolo image with Gunicorn + Uvicorn pre-configured
# ──────────────────────────────────────────────────────────────
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

# Set working directory inside the container
WORKDIR /app

# -------- install Python dependencies --------
COPY core/search/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN crawl4ai-setup

# -------- copy service code --------
RUN mkdir /app/search

# -------- runtime options (optional) --------
# Expose a default port (tiangolo listens on 80 inside the container)
CMD ["uvicorn", "search.api:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
