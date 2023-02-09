from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
import argparse
from urllib.request import urlretrieve


@task(log_prints=True, retries=1)
def download(color:str, year:int, month: int) -> pd.DataFrame:
    """Read taxi data from web into Dataframe"""
    urlretrieve(f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{color}_tripdata_{year}-{month:02}.csv.gz", 
                                f"{color}_tripdata_{year}-{month:02}.csv.gz")

    filename = f"{color}_tripdata_{year}-{month:02}.csv.gz"
    df = pd.read_csv(filename)

    print('the dataframe was loaded', len(df))

    return df, filename


@task(log_prints=True)
def upload_to_gcs(color: str, year: int, month: int, filename) -> Path:
    """Upload yellow trip data from GCS"""
    gcs_path = f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    # gcs_path = urlretrieve(f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{color}_tripdata_{year}-{month}.csv.gz", 
    #                             f"{color}_tripdata_{year}-{month}.gz")
    gcs_block = GcsBucket.load("zoom-gcp")
    gcs_block.upload_from_path(filename, f"{color}/{year}")

    # gcs_block.get_directory(from_path=gcs_path, local_path=f"/")

    return Path(f"../{gcs_path}")


@task(log_prints=True) 
def write_bq(df: pd.DataFrame, tablename: str) -> None:
    """Write DataFrame to Big Query"""

    gcp_credentials_block = GcpCredentials.load("zoom-gcp-creds")
    
    df.to_gbq(
        destination_table=f'dte-de-course-375014.trips_data_all.yellow_taxi_trips_{tablename}',
        project_id='dte-de-course-375014',
        credentials= gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append"
    )   

    rows = len(df)
    
    return print(f'taxi data loaded, there were {rows} rows processed succesfully!')

@flow(log_prints=True)
def etl_local_gcs_to_bq(color:str, year:int, months:list[int]):
    """Main ETL flow to load data to Big Query"""
    
    for month in months:
        df, filename = download(color, year, month)
        tablename= str(year)+'_'+str(month)
        upload_to_gcs(color, year, month, filename)
        write_bq(df, tablename)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='ETL taxi data web to GCS')
    parser.add_argument('--color', type=str, required=True, help='the color of the taxi data')
    parser.add_argument('--year', type=int, required=True, help='the year of the dataset')
    parser.add_argument('--months', type=list, required=True, help='the month of the dataset')
    args = parser.parse_args()

    etl_local_gcs_to_bq(color=args.color, year=args.year, months=args.months)
