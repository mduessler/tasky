variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "aws_region" {
  description = "AWS Region where all resources will be deployed"
  type        = string
}

variable "poject_name" {
  description = "Name of the project"
  type        = string
}

variable "runner_name" {
  description = "Unique name for this runner"
  type        = string
}
