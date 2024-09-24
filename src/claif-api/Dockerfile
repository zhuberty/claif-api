FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-alpine3.14-2024-03-11

RUN apk add --no-cache bash

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/wait-for-db-availability.sh

EXPOSE 8000

CMD ["bash", "-c", "./wait-for-db-availability.sh claif-db:5432 && uvicorn main:app --host 0.0.0.0 --port 8000"]
