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

variable "controller_instance_type" {
  description = "Hardware configuration for the controller instance."
  type        = string
}

variable "worker_instance_type" {
  description = "Hardware configuration for the worker instances."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC."
  type        = string
}

variable "workers" {
  description = "The set of worker nodes."
  type        = set(string)
}

variable "clustername" {
  description = "Name of the Kubernetes cluster."
  type        = string
}
