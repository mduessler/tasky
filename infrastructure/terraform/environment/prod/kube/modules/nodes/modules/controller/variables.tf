variable "availability_zone" {
  description = "Availability zone where resources will be deployed."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC."
  type        = string
}

variable "subnet_id" {
  description = "ID of the subnet to deploy the controller into."
  type        = string
}

variable "controller_profile_name" {
  description = "Name of the instance profile attached to the controller."
  type        = string
}

variable "instance_type" {
  description = "Hardware configuration for the controller instance."
  type        = string
}

variable "image_id" {
  description = "ID of the machine image."
  type        = string
}

variable "controller_sg_id" {
  description = "ID of the controller security group."
  type        = string
}

variable "worker_sg_id" {
  description = "ID of the worker security group."
  type        = string
}

variable "clustername" {
  description = "Name of the Kubernetes cluster."
  type        = string
}
