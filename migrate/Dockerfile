FROM python:3.12

WORKDIR /app

COPY migrate.py .

RUN pip install psycopg2-binary

CMD ["python", "migrate.py"]