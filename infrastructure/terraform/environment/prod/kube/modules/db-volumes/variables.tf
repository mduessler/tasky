variable "availability_zone" {
  description = "Availability Zone in which to deploy the volume"
  type        = string
}

variable "size" {
  description = "Configuration of the volume (sizes and names)"
  type        = number
}

variable "name" {
  description = "Suffic of the volume name"
  type        = string
}
