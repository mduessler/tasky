variable "backend_location" {
  description = "Location where the backend is deployed."
  type        = string
}

variable "environment" {
  description = "Target environment for this deployment."
  type        = string
}

variable "availability_zones" {
  description = "Availability zones where resources will be deployed."
  type        = list(string)
}

variable "clustername" {
  description = "Name of the cluster"
  type        = string
}
