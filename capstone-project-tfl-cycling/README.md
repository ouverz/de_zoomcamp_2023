## Course Project

With this project I was looking to analyze a subset of data published by Transport For London (TFL for short) - TFL Cycling data. TFL is a UK governement department responsible for much of London's transportation network including the London Tube, the Crossrail, Cycling routes etc.
The chosen dataset primarily monitors the usage of public bike rentals across the city supplied by Santander. The dataset is 
available online under [The TFL Cycling Dataset](https://cycling.data.tfl.gov.uk) with cycling utilisation data categorized under the 'Usage' folder in the
form of CSV files, each measuring data for a calendar week.


## Problem Statement

For the project, we will ask you to build a dashboard with two tiles. 

For that, you will need:

* Select a dataset that you're interested in (see [datasets.md](datasets.md))
* Create a pipeline for processing this dataset and putting it to a datalake
* Create a pipeline for moving the data from the lake to a data warehouse
* Transform the data in the data warehouse: prepare it for the dashboard
* Create a dashboard


## Data Pipeline 

The nature of this datset in terms of when data is published is unclear, hence the processing strategy I chose was batch ingestion. Batch processing not in its standard form as the data pipeline will not be scheudled to run at a certain frequency but at this time once only to load all available data. At the time of writing this document, I have not identified new data being published over a span of 3-4 weeks.. 

*note*: if we review the file naming convention, one would think new data would be published every week but that is not the case atm. 


![This is a alt text 1.](https://github.com/ouverz/de_zoomcamp_2023/main/capstone-project-tfl-cycling/images/data_pipeline_1.001.jpeg "This is a sample image 1.")

![This is a alt text 2.](https://github.com/ouverz/de_zoomcamp_2023/main/capstone-project-tfl-cycling/images/data_pipeline_1.002.jpeg "This is a sample image 2.")


### Tech Stack

* Cloud: Google Cloud Platform
* Infrastructure as Code (IaC): Terraform
* Workflow Orchestration: Airflow
* Data Wareshouse: BigQuery
* Batch Processing: Spark
* Data Transformation: Spark
* Data Visualisation: Metabase
* Version Control: Github


## Dashboard

You can build a dashboard with any of the tools shown in the course (Data Studio or Metabase) or any other BI tool of your choice. If you do use another tool, please specify and make sure that the dashboard is somehow accessible to your peers. 

Your dashboard should contain at least two tiles, we suggest you include:

- 1 graph that shows the distribution of some categorical data 
- 1 graph that shows the distribution of the data across a temporal line

Make sure that your graph is clear to understand by adding references and titles. 

Example of a dashboard: ![image](https://user-images.githubusercontent.com/4315804/159771458-b924d0c1-91d5-4a8a-8c34-f36c25c31a3c.png)


## Reproduce 
1. Fork and Clone the repository

2. Create a Google Cloud Platform account (a free trial is available).

3. Create a [Service Account](https://cloud.google.com/iam/docs/service-accounts-create) - through the Console menu via 'IAM & Admin' then select 'Service Accounts'. This account enables control and management of permissions to applications and 
compute engines rather than to individual accounts which increases security by creating that separation. After creating the account, one should retrieve an authentication key in order to connect seemlessly to GCP.

 3a - Download the authentication JSON file locally
 
 3b - Configure GCP credentials locally

    * 3b.1 Create a folder `.google/credentials` under the `${HOME}` directory and move the credentials file to that location.

    * 3b.2 Create environment variable and assign the JSON file authentication key
        ```
            export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-auth-keys>.json"
        ``` 

 3c - Confirm authentication and connection your local machine to GCP using your authentication key.
    ```
        # Refresh token/session, and verify authentication
        gcloud auth application-default login
    ``` 
4. Add necessary roles and enable the relevant APIs on the Service Account, this will enable the scripts and applications to communicate with Google Cloud Storage and BigQuery etc via their related APIs. 

 4a - Assign respective IAM Roles
   * 4a.1 Browse to 'IAM & Admin' then to 'IAM
    
   * 4a.2 Find the Service Account you created and click 'edit principal' on the right to add additionl roles. 
   * 4a.3 Add these roles -  Basic - Viewer, Storage Admin, Storage Cloud Admin, BigQuery Admin
    

 4b - Enable the following APIs
 
 Account credentials and IAM

* [IAM Account Credentials API](https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com)
* [Identity and Access Management (IAM) API](https://console.cloud.google.com/apis/library/iam.googleapis.com)


Google Storage and BigQuery

* [Cloud Storage API](https://console.cloud.google.com/apis/library/storage-component.googleapis.com)
    
* [BigQuery API](https://console.cloud.google.com/apis/library/bigquery.googleapis.com)


5.Install and setup Terraform (Infrastructure as Code) - this setup will create the infrastructure necessary for GCP including Storage Buckets and a BigQuery dataset.

The setup instructions can be found in the Terraform sub-directory markdown [terraform-setup](https://)

note*: If you are not familair with Terraform and do not want to work with it, please skip and configure these assets manually in the GCP UI.


6. Build Airflow and Apache Spark containers

 6a - Build the docker container for each application
```
    # Build the Apache Spark container with the tag 'spark-air'
    docker build -f Dockerfile.spark . -t spark-air
    
    # Build the Airflow container with the tag 'airflow-spark'
    docker build -f Dockerfile.airflow . -t airflow-spark
```

 6b - Run and deploy the applications - when successful, both applications will be accessible on your localmachine
```
    # Run the Apache Sparka and Airflow 
    docker-compose -f docker-compose.spark.yaml -f docker-compose.airflow.yaml up -d
```

7. Setup Airflow and run the DAGs

 7a - Add an Apache Spark connection - allows Airflow to communicate with the Spark cluster
 
 7b - Add the GCP authentication key as an environment variable - to enable connection to GCP
 
 7c - Run DAG - executing the data pipeline



## Going the extra mile - what's next...

* Add data fetching script
* Add data aggregation task
* Change dataset to include a more complex set that will allow modelling
* Add dbt
* Add tests
