FROM python:3.9

RUN apt-get update && apt-get install -y wget
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app

COPY data_ingestion.py data_ingestion.py 

ENTRYPOINT [ "python", "data_ingestion.py" ]