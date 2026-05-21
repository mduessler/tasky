variable "name" {
  description = "Unique Bucket name."
  type        = string
}

variable "version_status" {
  description = "Set the status of the versioning"
  type        = string
  default     = null
}
