variable "aws_region" {
  description = "AWS Region where all resources will be deployed."
  type        = string
}

variable "owner_id" {
  description = "ID of the owner."
  type        = string
}

variable "user_dev" {
  description = "Username of the user for development"
  type        = string
}
