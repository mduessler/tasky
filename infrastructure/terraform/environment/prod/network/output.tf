output "ids" {
  description = "Set of created vpc ids for the production"
  value       = { for az, vpc in module.vpcs : az => vpc.id }
}

output "private_subnets" {
  description = "Set of all created private subnet ids for the production"
  value       = { for az, vpc in module.vpcs : az => vpc.private_subnet }
}

output "controller_sg" {
  description = "Map of vpc id to controller security group id"
  value       = { for _, sg in aws_security_group.controllers : sg.vpc_id => sg.id }
}

output "worker_sg" {
  description = "Map of vpc id to worker security group id"
  value       = { for _, sg in aws_security_group.worker : sg.vpc_id => sg.id }
}
