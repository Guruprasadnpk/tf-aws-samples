terraform {
  backend "s3" {
    bucket = "gurppup"
    key    = "terraform/state/gcp_terraform.tfstate"
    region = "us-west-2"
    encrypt = true
  }
}
