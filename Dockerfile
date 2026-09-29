FROM python:3.13-slim

WORKDIR /app

# Install dependencies first so this layer is cached between code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hello.py .
COPY templates templates

ENV FLASK_APP=hello.py

EXPOSE 5000

# Bind to 0.0.0.0 so the server is reachable from outside the container
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
