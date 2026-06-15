variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "owner_id" {
  description = "ID of the account owner."
  type        = string
}

variable "aws_region" {
  description = "AWS Region where all resources will be deployed."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID."
  type        = number
}

variable "workers" {
  description = "The set of worker nodes"
  type        = set(string)
}

variable "clustername" {
  description = "Name of the cluster"
  type        = string
}
