from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
import pendulum



default_args = {
    'owner': 'airflow',    
    'retry_delay': timedelta(minutes=5)
}

BUCKET_NAME = 'tfl-cycling-data/pq'

with DAG("spark_dag",
        default_args=default_args,
        schedule=None,	
        dagrun_timeout=timedelta(minutes=60),
        description='use case of sparkoperator in airflow',
        start_date = pendulum.today('UTC').add(days=-1)
        
    ) as dag:

    Extract = GoogleCloudStorageToBigQueryOperator(
        task_id='extract', 
        bucket=BUCKET_NAME,
        source_objects=['*.parquet'],
        source_format='PARQUET',
        schema_fields=[
        {'name':'Rental_Id', 'type':'INTEGER', 'mode':'NULLABLE'},
        {'name':'Duration', 'type':'INTEGER', 'mode':'NULLABLE'},
        {'name':'Bike_Id', 'type':'INTEGER', 'mode':'NULLABLE'},
        {'name':'End_Date', 'type':'TIMESTAMP', 'mode':'NULLABLE'},
        {'name':'EndStation_Id', 'type':'INTEGER', 'mode':'NULLABLE'},
        {'name':'EndStation_Name', 'type':'STRING', 'mode':'NULLABLE'},
        {'name':'Start_Date', 'type':'TIMESTAMP', 'mode':'NULLABLE'},
        {'name':'StartStation_Id', 'type':'STRING', 'mode':'NULLABLE'},
        {'name':'StartStation_Name', 'type':'STRING', 'mode':'NULLABLE'}
        ],
        skip_leading_rows = 1,
        write_disposition='WRITE_APPEND',
        create_disposition='CREATE_IF_NEEDED',
        destination_project_dataset_table='dataengineering-384209.tfl_cycling.journies',
        allow_jagged_rows=True # allow for missing values 
    )

    TL = SparkSubmitOperator(
            application = "/opt/airflow/dags/pyspark_read_etl.py",
            jars="/opt/airflow/spark-lib/gcs-connector-hadoop3-2.2.5.jar,/opt/airflow/spark-lib/spark-3.3-bigquery-0.30.0.jar",
            conn_id= 'spark_default',
            task_id='transform_load'
            )

    Extract >> TL