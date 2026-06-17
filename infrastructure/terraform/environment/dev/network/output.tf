output "ids" {
  description = "Map of availability zones to VPC IDs."
  value       = { for az, vpc in module.vpcs : az => vpc.id }
}

output "private_subnets" {
  description = "Map of availability zones to private subnet IDs."
  value       = { for az, vpc in module.vpcs : az => vpc.private_subnet }
}
