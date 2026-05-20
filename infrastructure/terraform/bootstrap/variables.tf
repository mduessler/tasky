variable "aws_region" {
  description = "AWS Region where all resources will be deployed"
  type        = string
  default     = "eu-central-1"
}

variable "owner_id" {
  description = "ID of the owner"
  type        = string
}
