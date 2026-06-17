variable "environment" {
  description = "Target environment for this deployment."
  type        = string
}

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
