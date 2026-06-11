variable "ami_owners" {
  description = "Owner how owns the ami"
  type        = list(string)
  default     = ["self"]
}

variable "ami_filter_values" {
  description = "List of values, how to identify the ami"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
}

variable "subnet_id" {
  description = "ID of the subnet, should be private."
  type        = string
}

variable "security_groups" {
  description = "ID of the security group of the resource."
  type        = list(string)
}

variable "permission_profile" {
  description = "Name of the permission profile."
  type        = string
}

variable "http_hops" {
  description = "Number of hops allowed"
  type        = int
  default     = 2
}

variable "root_volume_size" {
  type    = number
  default = 20
}

variable "namespace" {
  description = "Namespace of the resource."
  type        = string
}

variable "identifier" {
  description = "Unique identifier of the resource."
  type        = string
}
