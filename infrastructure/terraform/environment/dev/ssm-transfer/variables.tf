variable "backend_location" {
  description = "Location where the backend is deployed."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "account_id" {
  description = "Unique identifier of the cloud account."
  type        = string
}
