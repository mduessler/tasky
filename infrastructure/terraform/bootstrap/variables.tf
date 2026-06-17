variable "backend_location" {
  description = "Location where the backend is deployed."
  type        = string
}

variable "account_id" {
  description = "Unique identifier of the cloud account."
  type        = string
}

variable "user_dev" {
  description = "Username of the development user."
  type        = string
}

variable "user_prod_network" {
  description = "Username of the production network user."
  type        = string
}

variable "user_prod_kube" {
  description = "Username of the production kube user."
  type        = string
}

variable "user_prod_packer" {
  description = "Username of the production packer user."
  type        = string
}
