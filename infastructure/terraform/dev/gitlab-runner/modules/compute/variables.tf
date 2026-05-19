# modules/compute/variables.tf

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "private_subnet_id" {
  description = "ID of the private subnet"
  type        = string
}

variable "runner_security_group_id" {
  description = "ID of the runner security group"
  type        = string
}

variable "instance_profile_name" {
  description = "IAM instance profile name"
  type        = string
}

variable "gitlab_runner_token" {
  description = "GitLab Runner registration token"
  type        = string
  sensitive   = true
}
