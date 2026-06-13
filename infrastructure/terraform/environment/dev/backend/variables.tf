variable "availability_zones" {
  description = "AWS Regions where to deploy the development backend"
  type        = list(string)
}

variable "environment" {
  description = "Deployment name of the environment."
  type        = string
  default     = dev
}

variable "owner_id" {
  description = "Owner id to create unique-bucket"
  type        = string
}
