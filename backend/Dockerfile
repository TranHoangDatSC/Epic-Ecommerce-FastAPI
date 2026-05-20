FROM python:3.13-slim
# Đã thêm postgresql-client vào dòng dưới:
RUN apt-get update && apt-get install -y libpq-dev gcc postgresql-client && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary
COPY backend/ .
COPY database/ /database_src/
CMD ["sh", "-c", "python /app/app/database/setup.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]