FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-alpine3.14-2024-03-11

COPY ./requirements.txt /app/requirements.txt
RUN python -m pip install -r requirements.txt
COPY ./main.py /app/main.py