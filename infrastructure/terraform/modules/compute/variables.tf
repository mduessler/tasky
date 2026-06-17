variable "instance_type" {
  description = "Hardware configuration for the instance."
  type        = string
}

variable "instance_profile" {
  description = "Name of the instance profile attached to the instance."
  type        = string
}

variable "image_owner" {
  description = "Owner of the machine image."
  type        = list(string)
}

variable "image_filter_values" {
  description = "List of values used to identify the machine image."
  type        = list(string)
}

variable "subnet_id" {
  description = "ID of the subnet to deploy the instance into."
  type        = string
}

variable "security_group_ids" {
  description = "List of security group IDs attached to the instance."
  type        = list(string)
}

variable "root_volume_size" {
  description = "Storage size of the root volume in GB."
  type        = number
}

variable "tags" {
  description = "Map of tags applied to the instance."
  type        = map(string)
}

variable "metadata_hop_limit" {
  description = "Maximum number of network hops allowed for instance metadata requests."
  type        = number
  default     = 1
}
