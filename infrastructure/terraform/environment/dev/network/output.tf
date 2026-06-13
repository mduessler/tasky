output "ids" {
  description = "Set of all created vpcs id for the development"
  value       = { for az, vpc in module.vpcs : az => vpc.id }
}

output "private_subnets" {
  description = "Set of all created private subnet ids for the development"
  value       = { for az, vpc in module.vpcs : az => vpc.private_subnet }
}
