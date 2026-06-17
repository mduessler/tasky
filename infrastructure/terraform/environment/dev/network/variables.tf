variable "backend_location" {
  description = "Location where the backend is deployed."
  type        = string
}

variable "availability_zones" {
  description = "AWS Regions where to deploy the development networks"
  type        = list(string)
}

variable "environment" {
  description = "Deployment name of the environment."
  type        = string
}
