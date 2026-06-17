variable "vpc_id" {
  description = "ID of the VPC."
  type        = string
}

variable "public_subnet_id" {
  description = "ID of the public subnet to deploy the load balancer into."
  type        = string
}

variable "workers" {
  description = "Map of worker names to instance IDs to register with the load balancer."
  type        = map(string)
}
