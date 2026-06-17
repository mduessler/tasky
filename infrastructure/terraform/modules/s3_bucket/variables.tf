variable "bucket_name" {
  description = "Unique name of the storage bucket."
  type        = string
}

variable "encryption_algorithm" {
  description = "Algorithm used to encrypt the bucket."
  type        = string
  default     = "AES256"
}

variable "block_public_access" {
  description = "Enables blocking of all public access to the bucket."
  type        = bool
  default     = true
}

variable "versioning_status" {
  description = "Versioning status of the bucket (Enabled, Suspended, or Disabled)."
  type        = string
  default     = null
}

variable "tags" {
  description = "Map of tags applied to the bucket."
  type        = map(string)
  default     = {}
}
