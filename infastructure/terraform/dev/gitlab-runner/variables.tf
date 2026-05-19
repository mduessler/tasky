variable "aws_region" {
  description = "AWS Region where all resources will be deployed"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "gitlab_runner_token" {
  description = "GitLab Runner registration token"
  type        = string
  sensitive   = true
}
