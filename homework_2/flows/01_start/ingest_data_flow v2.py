#!/usr/bin/env python
# coding: utf-8

import os
import argparse

from time import time

import pandas as pd
from sqlalchemy import create_engine
from prefect import flow, task

@task(log_prints=True)

def extract_data(url: str):
    #the backup files are gzipped, and it's important to keep the correct extension
    #for pandas to be able to open the file
    if url.endswith('.csv.gz'):
        csv_name = 'yellow_tripdata_2021-01.csv.gz'
    else:
        csv_name = 'output.csv' 

    path = os.getcwd()
    os.system(f"wget {url} -O {csv_name}")

    df_iter = pd.read_csv(path+'/'+ csv_name, iterator=True, chunksize=1800000)

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    return df


@task(log_prints=True)
def transform_data(df):
    print(f"pre: missing parameter count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    print(f"post: missing parameter count: {df['passenger_count'].isin([0]).sum()}")

    return df


@task(log_prints=True, retries=0)
def load_data(params, table_name, data):

    user = params['user']
    password = params['password']
    host = params['host']
    port = params['port']
    db = params['db']
    #table_name = params['table_name']
    df = data
    
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name=table_name, con=engine, if_exists='append')

@flow(name='Subflow', log_prints=True)
def log_subflow(table_name: str):
    print(f'Logging Subflow for: {table_name}')

@flow(name="Ingest Data")
def main_flow(table_name: str = 'yellow_taxi_trips'):
    args = {}
    args['user']='oferk'
    args['password']='root'
    args['host']='localhost' #'pgdatabase'
    args['port']='5432'
    args['db']='ny_taxi'
    args['url']='https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz'

    log_subflow(table_name)
    raw_data = extract_data(args['url'])
    data = transform_data(raw_data)
    load_data(args, table_name, data)

if __name__ == '__main__':
    main_flow(table_name='yellow_trips')