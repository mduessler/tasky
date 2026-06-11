variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "prod"
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "workers" {
  type    = set(string)
  default = ["01", "02"]
}

variable "aws_region" {
  description = "AWS Region where all resources will be deployed."
  type        = string
  default     = "eu-central-1"
}
