from prefect.deployments import Deployment
from etl_web_to_gcs import etl_web_to_gcs
from prefect.filesystems import GitHub 

storage = GitHub.load("zoom-github")
# entrypoint = "homework_2/flows/02_gcp/etl_web_to_gcs.py:etl_web_to_gcs"
entrypoint = "homework_2/flows/etl_web_to_gcs.py:etl_web_to_gcs"

deployment = Deployment.build_from_flow(
     flow=etl_web_to_gcs,
     name="github-example",
     storage=storage,
     entrypoint=entrypoint)

if __name__ == "__main__":
    deployment.apply()