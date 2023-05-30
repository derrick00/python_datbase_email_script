FROM python:3.10.10-alpine

WORKDIR /database

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "script.py"]