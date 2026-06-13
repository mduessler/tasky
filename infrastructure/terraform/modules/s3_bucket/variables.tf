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

variable "sse_algorithm" {
  description = "Algorithm to encrypt the s3 bucket"
  type        = string
  default     = "AES256"
}

variable "block_public_access" {
  description = "Define the block of the public access"
  type        = bool
  default     = true
}
