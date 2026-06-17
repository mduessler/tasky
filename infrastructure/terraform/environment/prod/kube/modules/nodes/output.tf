output "vpc_id" {
  description = "ID of the VPC."
  value       = var.vpc_id
}

output "controller_endpoint" {
  description = "DNS name of the internal load balancer for the controller API server."
  value       = module.controller.endpoint
}

output "workers" {
  description = "Map of worker names to instance IDs."
  value       = { for k, mod in module.workers : k => mod.id }
}
