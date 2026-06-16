output "vpc_id" {
  description = "VPC ID of the network in which the kubes operate."
  value       = var.vpc_id
}

output "controller" {
  description = "ID of the controller instance."
  value       = module.controller_id
}

output "workers" {
  description = "List of the worker instances IDs."
  value       = [for mod in module.workers : mod.instance_id]
}
