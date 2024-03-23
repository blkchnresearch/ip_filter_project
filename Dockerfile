FROM python:3.9-slim

WORKDIR /app
COPY . /app

# Copy SSL certificate files
COPY server.crt /app
COPY server.key /app

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "backend.py"]

