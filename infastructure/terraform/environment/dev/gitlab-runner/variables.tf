variable "aws_region" {
  description = "AWS Region where all resources will be deployed"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "poject_name" {
  description = "Name of the project"
  type        = string
}

variable "runner_name" {
  description = "Unique name for this runner"
  type        = string
}
