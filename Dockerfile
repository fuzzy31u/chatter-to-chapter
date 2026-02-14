FROM python:3.12-slim

WORKDIR /app

COPY chatter_to_chapter/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt uvicorn

COPY chatter_to_chapter/ ./chatter_to_chapter/
COPY main.py .
COPY web/ ./web/

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
