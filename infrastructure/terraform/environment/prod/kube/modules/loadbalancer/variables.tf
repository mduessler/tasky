variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}
variable "public_subnet" {
  description = "ID of the private subnet"
  type        = string
}
variable "workers" {
  description = "List of workers"
  type        = list(string)
}
