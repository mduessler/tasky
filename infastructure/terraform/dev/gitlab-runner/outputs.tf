output "vpc_id" {
  description = "ID of the VPC"
  value       = module.networking.vpc_id
}

output "subnet_id" {
  description = "ID of the private subnet"
  value       = module.networking.subnet_id
}

output "runner_security_group_id" {
  description = "ID of the runner security group"
  value       = module.networking.runner_security_group_id
}
