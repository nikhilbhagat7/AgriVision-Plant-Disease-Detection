# lightweight Python image
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PIL, torch.... and clean cache for smaller docker file  
RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "10000"]