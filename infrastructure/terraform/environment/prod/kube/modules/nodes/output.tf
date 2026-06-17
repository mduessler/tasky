output "vpc_id" {
  description = "ID of the VPC."
  value       = var.vpc_id
}

output "controller" {
  description = "ID of the controller instance."
  value       = module.controller.id
}

output "workers" {
  description = "List of worker instance IDs."
  value       = [for mod in module.workers : mod.id]
}
