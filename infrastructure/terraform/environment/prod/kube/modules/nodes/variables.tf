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

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID."
  type        = string
}

variable "workers" {
  description = "The set of worker nodes"
  type        = set(string)
}

variable "clustername" {
  description = "Name of the cluster"
  type        = string
}
