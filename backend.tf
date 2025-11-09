terraform {
  backend "s3" {
    bucket = "gurppup"
    key    = "terraform/state/terraform.tfstate"
    region = "us-west-2"
    encrypt = true
  }
}
