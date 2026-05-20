variable "bucket_id" {
  description = "S3 Bucket ID"
  type        = string
}

variable "policy_statements" {
  description = "List of policy statements"
  type        = any
}
