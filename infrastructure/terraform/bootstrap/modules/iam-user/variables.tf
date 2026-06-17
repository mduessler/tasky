variable "backend_location" {
  description = "Location where the backend is deployed."
  type        = string
}

variable "account_id" {
  description = "Unique identifier of the cloud account."
  type        = string
}

variable "user_name" {
  description = "Name of the IAM user to create."
  type        = string
}

variable "policies" {
  description = "Path to the folder containing the policy JSON files."
  type        = string
}
