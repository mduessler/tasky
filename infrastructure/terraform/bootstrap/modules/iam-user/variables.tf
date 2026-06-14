variable "user_name" {
  description = "Name des anzulegenden IAM-Users"
  type        = string
}

variable "policies" {
  description = "Pfad zum Ordner mit den Policy-JSON-Dateien"
  type        = string
}
