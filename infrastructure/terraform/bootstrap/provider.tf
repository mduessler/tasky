terraform {
  required_version = ">= 1.15.3"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "tasky-terraform-state-REDACTED_AWS_ACCOUNT-dev"
    key            = "bootstrap/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "tasky-terraform-locks-dev"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "tasky"
      Environment = "dev"
      ManagedBy   = "terraform"
    }
  }
}
