FROM python:3.11-slim

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Install requirements first for better caching
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir -e ".[backend]"

# Copy application code
# COPY . ./fileraven/backend

EXPOSE 8000

CMD ["uvicorn", "fileraven.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]