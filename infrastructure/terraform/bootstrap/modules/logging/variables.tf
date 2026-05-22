variable "target_id" {
  description = "The ID of the S3 bucket to enable logging for."
  type        = string
}

variable "target_arn" {
  description = "The arn of the S3 bucket to enable logging for."
  type        = string
}

variable "owner_id" {
  description = "ID of the owner."
  type        = string
}
