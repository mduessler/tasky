output "tf_state_dev" {
  description = "ID of the Terraform state bucket for the dev environment."
  value       = module.tf_state_dev.id
}

output "tf_state_prod" {
  description = "ID of the Terraform state bucket for the prod environment."
  value       = module.tf_state_prod.id
}
