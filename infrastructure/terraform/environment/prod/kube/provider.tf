terraform {
  required_version = ">= 1.15.3"
  backend "s3" {
    region       = "eu-central-1"
    use_lockfile = true
    encrypt      = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

locals {
  tags = {
    Project     = "tasky"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = local.tags
  }
}
