# FROM python:3.10-slim

# # Install system dependencies for LightGBM
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libgomp1 \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8000

# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.10-slim

WORKDIR /app

# Copy requirements from backend folder
COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ backend/

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
