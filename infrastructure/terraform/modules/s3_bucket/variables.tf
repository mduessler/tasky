variable "name" {
  description = "Unique Bucket name."
  type        = string
}

variable "version_status" {
  description = "Set the status of the versioning."
  type        = string
  default     = null
}

variable "tags" {
  description = "Resource-level tags merged with the provider's default_tags."
  type        = map(string)
  default     = {}
}
