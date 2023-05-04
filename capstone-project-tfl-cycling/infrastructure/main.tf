terraform {
  required_version = ">= 1.0"
  backend "local" {}
  required_providers {
    google = { 
      source  = "hashicorp/google"
    }

    docker = { 
      source  = "kreuzwerker/docker"
      version = "2.15.0"
    }
  }
}

provider "google" {
  project = var.project
  region = var.region
  // credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}


# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "tfl-cycling-auto" {
  name                        = "${local.data_lake_bucket}_${var.project}" # Concatenating DL bucket & Project name for unique naming
  location                    = var.region
  # Optional, but recommended settings:
  storage_class               = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

# DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.BQ_DATASET
  project    = var.project
  location   = var.region
}

# Airflow application
resource "docker_image" "airflow" {
  name = "airflow-spark"

  build {
      path = "./../docker_airflow"
      dockerfile = "Dockerfile.airflow"
  }

}


# Spark application
resource "docker_image" "apache-spark" {
  name = "spark-air"

  build {
      path = "./../docker_airflow"
      dockerfile = "Dockerfile.spark"
  }

}

# Optional: VPC Network
# resource "google_compute_network" "vpc_network" {
#   name = "terraform-network"
# }


# Optional: VM Instance to host Airflow and Spark applications
# resource "google_compute_instance" "vm_instance" {
#   name         = "terraform-instance"
#   machine_type = "f1-micro"
#   tags         = ["web", "dev"]

#   boot_disk {
#     initialize_params {
#       image = "cos-cloud/cos-stable"
#     }
#   }

#   network_interface {
#     network = google_compute_network.vpc_network.name
#     access_config {
#     }
#   }
# }

