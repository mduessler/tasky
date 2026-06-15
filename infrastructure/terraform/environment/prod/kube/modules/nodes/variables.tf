variable "vpc_id" {
  description = "VPC ID."
  type        = number
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
}

variable "availability_zone" {
  description = "Availability zone in which to create the nodes"
  type        = string
}

variable "controller" {
  description = "The name of the controller node"
  type        = string
}

variable "workers" {
  description = "The set of worker nodes"
  type        = set(string)
}

variable "clustername" {
  description = "Name of the cluster"
  type        = string
}
