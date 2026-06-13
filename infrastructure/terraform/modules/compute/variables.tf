variable "ami_owners" {
  description = "Owner how owns the ami"
  type        = list(string)
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

variable "iam_instance_profile" {
  description = "Name of the permission profile."
  type        = string
}

variable "http_hops" {
  description = "Number of hops allowed"
  type        = number
  default     = 1
}

variable "root_volume_size" {
  description = "Storage size for the volume."
  type        = number
}

variable "tags" {
  description = "Map of tags to adapt to the instance"
  type        = map(string)
}
