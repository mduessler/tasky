variable "availability_zone" {
  description = "Availability zone where resources will be deployed."
  type        = string
}

variable "sizes" {
  description = "Sizes of the volumes in GB."
  type        = list(number)
}

variable "names" {
  description = "Suffix of the volume name."
  type        = list(string)
}
