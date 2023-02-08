#!/usr/bin/env python
# coding: utf-8

import os
import argparse
import wget

from time import time

import pandas as pd
from sqlalchemy import create_engine


def main(params):

    user = args['user']
    password = args['password']
    host = args['host=']
    port = args['port']
    db = args['db']
    table_name = args['table_name']
    url = args['url']
    
    #the backup files are gzipped, and it's important to keep the correct extension
    #for pandas to be able to open the file
    file = wget.download(url)
    # print('this is the file', filename)
    if url.endswith('.csv.gz'):
        csv_name = 'yellow_tripdata_2021-01.csv.gz'
    else:
        csv_name = 'yellow_tripdata_2021-01.csv'

    os.system(f"wget {url} -O {csv_name}")

    # csv_name = 'yellow_tripdata_2021-01.csv'

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(file, iterator=True, chunksize=100000)

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name=table_name, con=engine, if_exists='append')


    while True: 

        try:
            t_start = time()
            
            df = next(df_iter)

            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()

            print('inserted another chunk, took %.3f second' % (t_end - t_start))

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break

if __name__ == '__main__':
    args = {}
    args['user']='root'
    args['password']='root'
    args['host=']='localost'
    args['port']='5432'
    args['db']='ny_taxi'
    args['table_name']='yellow_taxi_trips'
    args['url']='https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz'


    main(args)