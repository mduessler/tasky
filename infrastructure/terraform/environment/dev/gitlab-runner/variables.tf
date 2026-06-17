variable "backend_location" {
  description = "Location where the backend is deployed."
  type        = string
}

variable "environment" {
  description = "Target environment for this deployment."
  type        = string
}

variable "account_id" {
  description = "Unique identifier of the cloud account."
  type        = string
}

variable "availability_zone" {
  description = "Availability zone where resources will be deployed."
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
