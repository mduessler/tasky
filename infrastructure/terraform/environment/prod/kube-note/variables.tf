variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "prod"
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.mikro"
}

variable "workers" {
  type    = set(string)
  default = ["01", "02"]
}
