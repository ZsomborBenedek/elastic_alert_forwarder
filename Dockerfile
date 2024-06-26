FROM python:3.12-slim

WORKDIR /forwarder

COPY ./app/requirements.txt /forwarder/app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r app/requirements.txt

COPY ./app /forwarder/app

CMD [ "python3", "app/main.py" ]
