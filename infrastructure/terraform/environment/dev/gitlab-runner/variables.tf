variable "aws_region" {
  description = "AWS Region where the backend is deployed."
  type        = string
}

variable "availability_zone" {
  description = "Zone in which VPC the runner should be deployed"
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
}

variable "runner_name" {
  description = "Unique name for this runner."
  type        = string
}

variable "owner_id" {
  description = "ID of the owner."
  type        = string
}
