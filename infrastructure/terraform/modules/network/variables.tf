variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "aws_region" {
  description = "AWS Region where the network will be deployed."
  type        = string
}

variable "private_tags" {
  description = "Tags of the private subnet"
  type        = map(string)
  default     = {}
}

variable "public_tags" {
  description = "Tags of the public_tags subnet"
  type        = map(string)
  default     = {}
}
