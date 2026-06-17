output "ids" {
  description = "Map of availability zones to VPC IDs."
  value       = { for az, vpc in module.vpcs : az => vpc.id }
}

output "private_subnets" {
  description = "Map of VPC IDs to private subnet IDs."
  value       = { for _, vpc in module.vpcs : vpc.id => vpc.private_subnet }
}

output "public_subnets" {
  description = "Map of VPC IDs to public subnet IDs."
  value       = { for _, vpc in module.vpcs : vpc.id => vpc.public_subnet }
}

output "controller_sgs" {
  description = "Map of VPC IDs to controller security group IDs."
  value       = { for _, sg in aws_security_group.controllers : sg.vpc_id => sg.id }
}

output "worker_sgs" {
  description = "Map of VPC IDs to worker security group IDs."
  value       = { for _, sg in aws_security_group.worker : sg.vpc_id => sg.id }
}
