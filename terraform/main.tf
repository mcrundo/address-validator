terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket       = "address-validation-tf-state"
    key          = "dev/terraform.tfstate"
    region       = "us-east-2"
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "address-validation"
      Environment = var.environment
      ManagedBy   = "terraform"
      Repository  = "address-validation-service"
    }
  }
}
