variable "aws_region" {
  description = "AWS Region where all resources will be deployed."
  type        = string
  default     = "eu-central-1"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "runner_name" {
  description = "Unique name for this runner."
  type        = string
}

variable "owner_id" {
  description = "ID of the owner."
  type        = string
}
