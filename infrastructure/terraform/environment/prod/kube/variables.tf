variable "availability_zones" {
  description = "AWS Regions where to deploy the development networks"
  type        = list(string)
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "prod"
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "workers" {
  type    = set(string)
  default = ["01", "02"]
}

variable "aws_region" {
  description = "AWS Region where all resources will be deployed."
  type        = string
  default     = "eu-central-1"
}

variable "clustername" {
  description = "Name of the cluster"
  type        = string
}

variable "owner_id" {
  description = "ID of the account owner."
  type        = string
}

variable "workers_by_availability_zone" {
  description = "Mapping of zone to the names of the workers"
  type = map(object({
    instance_type = string
    nodes         = list(string)
  }))

  default = {
    "eu-central-1a" = {
      instance_type = "node-group-a"
      nodes         = ["node-a1", "node-a2"]
    }
    "eu-central-1b" = {
      name  = "node-group-b"
      nodes = ["node-b1"]
    }
  }
}
