#!/usr/bin/env python
# coding: utf-8

import os
import argparse

from time import time

import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect.filesystems import GitHub
from pathlib import Path

@task(log_prints=True)
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into Dataframe"""

    df = pd.read_csv(dataset_url)

    return df

@task(log_prints=True)
def clean(df = pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""

    df['tpep_pickup_dataetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_dataetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

    return df

@task()
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Write dataframe out locally as a parquet file"""
    path = Path(f"data/{ color}/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    
    return path


@task()
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.upload_from_path(
        from_path=f"{path}", to_path=path 
    )

    return
    

@flow()
def etl_web_to_gcs() -> None:
    """The main ETL function"""
    color = "yellow"
    year = 2021
    month = 1
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"
    
    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    print('the path returned is: ', path )
    write_gcs(path)

@task()
def fetch_code():
    github_block = GitHub.load("zoom-github")


if __name__ == '__main__':
    etl_web_to_gcs()