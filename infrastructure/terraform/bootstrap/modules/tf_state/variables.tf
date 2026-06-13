variable "aws_region" {
  description = "AWS Region where all resources will be deployed."
  type        = string
}

variable "environment" {
  description = "Environment for which to deploy the backend"
  type        = string

}

variable "owner_id" {
  description = "ID of the owner."
  type        = string
}
