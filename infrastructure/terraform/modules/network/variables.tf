variable "availability_zone" {
  description = "Availability zone where resources will be deployed."
  type        = string
}

variable "environment" {
  description = "Target environment for this deployment."
  type        = string
}

variable "vpc_cidr" {
  description = "IP range for the VPC in CIDR notation."
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnet_tags" {
  description = "Tags applied to the private subnet."
  type        = map(string)
  default     = {}
}

variable "public_subnet_tags" {
  description = "Tags applied to the public subnet."
  type        = map(string)
  default     = {}
}
