terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.67"
    }
  }

  backend "s3" {
    bucket         = "photo-ranker-terraform-state"
    region         = "us-east-2"
    key            = "terraform/terraform.tfstate"
    encrypt        = true
    dynamodb_table = "photo-ranker-terraform-lock"
  }
  required_version = ">= 1.2.0"
}
provider "aws" {
  region = "us-east-2"
}
