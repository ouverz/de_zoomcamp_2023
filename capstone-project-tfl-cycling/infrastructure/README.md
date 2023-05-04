### Installation 
# Download/Install Terraform (OSX - Homebrew)
Install HashiCorp tap repo and related packages
Note: you can also download an executable here: https://developer.hashicorp.com/terraform/downloads

brew upgrade hashicorp/tap/terraform
```

Install Terraform
brew install hashicorp/tap/terraform
```

Update Homebrew so that you can update to the latest Terraform version available
brew update
```

Run the upgrade bommand to install the latest Terraform version
brew upgrade hashicorp/tap/terraform
```

# Initialize state file (.tfstate)
terraform init

# Check changes to new infra plan
terraform plan
```
Please enter the GCP Project ID you have created for this project (this value will be used
throughout this project). Alternatively, you may add an argument variables in the form:
-var="project=<your-gcp-project-id>"


```shell
# Create the new infrastructure (bucket, BigQuery dataset)
terraform apply -var="project=<your-gcp-project-id>"
```

```shell
# Delete infra after your work, to avoid costs on any running services
terraform destroy
```