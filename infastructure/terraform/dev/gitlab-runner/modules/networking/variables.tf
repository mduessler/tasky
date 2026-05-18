variable "vpc_cidr" {
  description = "IP block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}
variable "aws_region" {
  description = "AWS Region"
  type        = string
}
variable "environment" {
  description = "Deployment environment"
  type        = string
}
