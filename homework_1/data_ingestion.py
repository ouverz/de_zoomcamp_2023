import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import argparse

import os
from time import time


def main(args):

    user = args.user
    password = args.password
    host = args.host
    port = args.port
    database = args.database
    tablename = args.tablename
    url = args.url

    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'

    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    df = next(df_iter)

    df.head(n=0).to_sql(name=tablename, con=engine, if_exists='replace')

    df.to_sql(name=tablename, con=engine, if_exists='append')

    while True: 

        try:
            t_start = time()
            
            df = next(df_iter)

            df.to_sql(name=tablename, con=engine, if_exists='append')

            t_end = time()

            print('inserted another chunk, took %.3f second' % (t_end - t_start))

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data')

    parser.add_argument('--user', required=True, help='username for Postgres')
    parser.add_argument('--password', required=True, help='User password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--database', required=True, help='database for postgres')
    parser.add_argument('--tablename', required=True, help='tablename for postgres')
    parser.add_argument('--url', required=True, help='url to download csv file')


    args = parser.parse_args()

    main(args)
