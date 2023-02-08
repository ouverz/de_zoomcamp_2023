from prefect.deployments import Deployment
from etl_web_to_gcs import etl_web_to_gcs
from prefect.filesystems import GitHub 

storage = GitHub.load("zoom-github")

deployment = Deployment.build_from_flow(
     flow=etl_web_to_gcs,
     name="github-example",
     storage=storage,
     entrypoint="https://github.com/ouverz/de_zoomcamp_2023/tree/main/homework_2/flows/02_gcp/etl_web_to_gcs_.py:etl_web_to_gcs")

if __name__ == "__main__":
    deployment.apply()