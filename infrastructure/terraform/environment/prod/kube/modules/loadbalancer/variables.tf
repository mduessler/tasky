variable "vpc_id" {
  description = "ID of the VPC."
  type        = string
}

variable "public_subnet_id" {
  description = "ID of the public subnet to deploy the load balancer into."
  type        = string
}

variable "workers" {
  description = "List of worker instance IDs to register with the load balancer."
  type        = list(string)
}
