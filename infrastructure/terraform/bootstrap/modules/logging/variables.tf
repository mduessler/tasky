variable "account_id" {
  description = "Unique identifier of the cloud account."
  type        = string
}

variable "target_id" {
  description = "The ID of the S3 bucket to enable logging for."
  type        = string
}

variable "target_arn" {
  description = "The arn of the S3 bucket to enable logging for."
  type        = string
}

variable "environment" {
  description = "Environment for which to deploy the backend"
  type        = string
}
