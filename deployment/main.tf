terraform {
  backend "s3" {
    bucket = "wltdo-tf-state"
    region = "us-east-1"
    key    = "wltdo-backend/terraform.tfstate"
  }
}

provider "aws" {
  region = "us-east-1"
}

variable cloudfront_secret {
  description = "The secret that cloud front will send to api gateway"
  type        = string
}
