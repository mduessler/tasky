variable "name" {
  description = "Unique Bucket name."
  type        = string
}

variable "prevent_destroy" {
  description = "Enable or disable deletion of bucket, if it is new initialized."
  type        = string
  default     = True
}
