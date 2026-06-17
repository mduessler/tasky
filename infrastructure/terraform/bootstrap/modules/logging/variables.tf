variable "environment" {
  description = "Target environment for this deployment."
  type        = string
}

variable "account_id" {
  description = "Unique identifier of the cloud account."
  type        = string
}

variable "target_bucket_id" {
  description = "ID of the target storage bucket to log to."
  type        = string
}

variable "target_bucket_arn" {
  description = "ARN of the target storage bucket to log to."
  type        = string
}
