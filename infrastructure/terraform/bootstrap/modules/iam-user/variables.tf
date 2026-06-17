variable "backend_location" {
  description = "Location where the backend is deployed."
  type        = string
}

variable "owner_id" {
  description = "ID of the owner."
  type        = string
}

variable "user_name" {
  description = "Name des anzulegenden IAM-Users"
  type        = string
}

variable "policies" {
  description = "Pfad zum Ordner mit den Policy-JSON-Dateien"
  type        = string
}
