variable "aws_region" {
  description = "AWS Region where all resources will be deployed"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string  # "dev", "staging", "prod"
}

