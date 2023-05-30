FROM python:3.10.10-alpine

WORKDIR /database

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./


CMD ["python", "script.py"]