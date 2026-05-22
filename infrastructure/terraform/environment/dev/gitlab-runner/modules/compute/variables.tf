variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
}

variable "subnet_id" {
  description = "ID of the subnet, should be private."
  type        = string
}

variable "runner_security_group" {
  description = "ID of the security group for the runner."
  type        = string
}

variable "permission_profile" {
  description = "Name of the permisions for the machine."
  type        = string
}

variable "runner_name" {
  description = "Unique name for this runner."
  type        = string
}
