variable "availability_zones" {
  description = "AWS Regions where to deploy the development networks"
  type        = list(string)
}

variable "environment" {
  description = "Deployment name of the environment."
  type        = string
}

variable "aws_region" {
  description = "Deployment name of the environment."
  type        = string
}
