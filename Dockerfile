# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY . .
RUN pip install -r requirements.txt
RUN python app/init_db.py
CMD ["python", "app.py"]
