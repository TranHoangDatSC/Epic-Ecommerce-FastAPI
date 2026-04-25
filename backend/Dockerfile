FROM python:3.13-slim

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt thư viện
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary

# Copy ruột folder backend vào /app
COPY backend/ .

# Copy folder database (ngang hàng backend ở ngoài) vào /database_src ở gốc container
COPY database/ /database_src/

# Chạy đúng file setup.py nằm trong app/database/
CMD ["sh", "-c", "python /app/app/database/setup.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]