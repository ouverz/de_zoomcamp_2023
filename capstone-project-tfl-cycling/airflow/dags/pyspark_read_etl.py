from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import functions as F

import pandas as pd


conf = SparkConf() \
    .setMaster('local') \
    .setAppName('test') \
    .set("spark.jars", "/opt/airflow/spark-lib/spark-3.3-bigquery-0.30.0.jar") \
    .set("spark.jars", "/opt/airflow/spark-lib/gcs-connector-hadoop3-2.2.5.jar") \
    .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", '/opt/bitnami/spark/.google/credentials/google_credentials.json') \
    .set("viewsEnabled","true") \
    .set("materializationDataset","dataengineering-384209:tfl_cycling")


sc = SparkContext(conf=conf.set("spark.files.overwrite", "true"))

hadoop_conf = sc._jsc.hadoopConfiguration()

hadoop_conf.set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
hadoop_conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
hadoop_conf.set("fs.gs.auth.service.account.json.keyfile", '/opt/bitnami/spark/.google/credentials/google_credentials.json')
hadoop_conf.set("fs.gs.auth.service.account.enable", "true")


spark = SparkSession.builder \
    .config(conf=sc.getConf()) \
    .getOrCreate()


def read_parquet(path) -> pd.DataFrame:
    """
     Reading Parquet files recursively from bucket and appending
     the data to a Spark Dataframe
    """
    try: 
        df_test = spark.read.option("recursiveFileLookup", "true").parquet(path)
        
        print('Successfully read the dataframe')
        return df_test
    
    except Exception as err:
        print('There was an error once loading the data in Spark', err)
    

def read_table(table_id):
    """
     Reading data from BiqQuery table and loading 
     the data into a Spark Dataframe
    """
    try:
        df = spark.read \
        .format("bigquery") \
        .option("table", table_id) \
        .option("credentialsFile", "/opt/airflow/.google/credentials/google_credentials.json") \
        .option("parentProject", "dataengineering-384209") \
        .load()

        return df

    except Exception as err:
        print(f'There was an error reading from {table_id}: ', err)


def transform_data(df) -> pd.DataFrame:
    """
     Transforming the data inside the Spark Dataframe such that
     the 'Start Date' and 'End Date' are converted from String format
     to a datetime format. Also, any records without 'StartStation Name' 
     will be removed before appending the remaining records
     into a Spark Dataframe
    """
    # Convert String columns ['Start Date', 'End Date'] to Timestamp
    df_transformed = df.withColumn("Start_Date", F.to_timestamp(F.col("Start_Date"), "M/d/yyyy H:mm")) \
                       .withColumn("End_Date", F.to_timestamp(F.col("End_Date"), "M/d/yyyy H:mm"))

    # Remove records from dataframe where 'StartStation Name' is NULL - as we want to maintain
    # a consistent and complete dataset for analysis
    df_filtered = df_transformed.filter(df_transformed['StartStation_Name'] != 'null')

    return df_filtered


def load_to_bq(df) -> pd.DataFrame:
    """
      Write the transformed records from the Spark Dataframe
      to a BigQuery table - creating a Staging layer
    """

    try:
        #Write report result to BigQuery<
        df.write.format("bigquery") \
                .option("table", "tfl_cycling.staging_journies") \
                .option("credentialsFile", "/opt/airflow/.google/credentials/google_credentials.json") \
                .option("parentProject", "dataengineering-384209") \
                .option("writeMethod","direct") \
                .mode("append") \
                .save()
        # .option("writeMethod","direct") \
        # .option("temporaryGcsBucket","temporary_bucket_spark") \
        print(f'There were {df.count()} records loaded succesfully to BigQuery')
    except Exception as err:
        print('There was an error when loading records to BigQuery: ', err)
    

if __name__ == '__main__':
    
    df = read_table(table_id='tfl_cycling.journies')
    df_transformed = transform_data(df)
    load_to_bq(df_transformed)
