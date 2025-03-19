FROM python:3.12


WORKDIR /code


COPY ./app/requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./app/ /code/app/
ENV JWT_SECRET_KEY="very_secret_key"
ENV TASK_FREQUENCY_IN_SECONDS="60"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
