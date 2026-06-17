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
  description = "Availability zones where resources will be deployed."
  type        = list(string)
}

variable "workers" {
  description = "The set of worker nodes."
  type        = set(string)
  default     = ["01", "02"]
}

variable "clustername" {
  description = "Name of the Kubernetes cluster."
  type        = string
}

variable "workers_by_availability_zones" {
  description = "Mapping of zone to the names of the workers"
  type = map(object({
    controller_instance_type = string
    worker_instance_type     = string
    nodes         = list(string)
    postgres_volumes = object({
      sizes = list(number)
      names = list(string)
    })
    etcd_volumes = object({
      sizes = list(number)
      names = list(string)
    })
  }))
}
