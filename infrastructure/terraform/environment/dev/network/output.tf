output "ids" {
  description = "Map of availability zones to VPC IDs."
  value       = { for az, vpc in module.vpcs : az => vpc.id }
}

output "private_subnets" {
  description = "Map of VPC IDs to private subnet IDs."
  value       = { for _, vpc in module.vpcs : vpc.id => vpc.private_subnet }
}
