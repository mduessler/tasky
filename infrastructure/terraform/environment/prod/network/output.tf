output "ids" {
  description = "Set of created vpcs id for the production"
  value       = { for az, vpc in module.vpcs : az => vpc.id }
}

output "private_subnets" {
  description = "Set of all created private subnets id for the production"
  value       = { for az, vpc in module.vpcs : az => vpc.private_subnet }
}
