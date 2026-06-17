variable "availability_zone" {
  description = "Availability Zone in which to deploy the volume"
  type        = string
}

variable "sizes" {
  description = "Configuration of the volume (sizes and names)"
  type        = list(number)
}

variable "names" {
  description = "Suffic of the volume name"
  type        = list(string)
}
