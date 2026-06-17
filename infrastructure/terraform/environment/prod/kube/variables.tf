variable "backend_location" {
  description = "Location where the backend is deployed."
  type        = string
}

variable "environment" {
  description = "Target environment for this deployment."
  type        = string
  default     = "prod"
}

variable "account_id" {
  description = "Unique identifier of the cloud account."
  type        = string
}

variable "availability_zones" {
  description = "AWS Regions where to deploy the development networks"
  type        = list(string)
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

variable "clustername" {
  description = "Name of the cluster"
  type        = string
}

variable "workers_by_availability_zone" {
  description = "Mapping of zone to the names of the workers"
  type = map(object({
    instance_type = string
    nodes         = list(string)
    db_volumes = object({
      sizes = list(number)
      names = list(string)
    })
  }))
}
