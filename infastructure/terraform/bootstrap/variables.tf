variable "aws_region" {
  description = "AWS Region where all resources will be deployed"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "owner_id" {
  description = "ID of the owner"
  type        = string
}
