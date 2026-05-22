variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "runner_name" {
  description = "Unique name for this runner."
  type        = string
}

variable "ssm_bucket_arn" {
  type = string
}
