variable "name" {
  description = "Unique Bucket name."
  type        = string
}

variable "prevent_destroy" {
  description = "Enable or disable deletion of bucket, if it is new initialized."
  type        = bool
}

variable "version_status" {
  description = "Set the status of the versioning"
  type        = string
}
