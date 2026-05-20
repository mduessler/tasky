variable "username" {
  description = "Usernam of the tasky-gitlab-runner IAM user"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "policies" {
  description = "Polcies to assign to user"
  type        = list(string)
  default     = []
}

variable "poject_name" {
  description = "Name of the project"
  type        = string
}
