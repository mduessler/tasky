terraform {
  required_version = ">= 1.15.3"
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
  alias  = "frankfurt"
  region = "eu-central-1"
  default_tags {
    tags = local.tags
  }
}
