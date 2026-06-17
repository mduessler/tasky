variable "availability_zone" {
  description = "Availability zone where resources will be deployed."
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
