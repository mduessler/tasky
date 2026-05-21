variable "environment" {
  description = "Environment name"
  type        = string
}

variable "tags" {
  description = "Resource-level tags merged with the provider's default_tags."
  type        = map(string)
  default     = {}
}
