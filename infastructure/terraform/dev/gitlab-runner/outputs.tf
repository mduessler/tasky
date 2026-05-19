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

output "instance_profile_name" {
  description = "IAM instance profile name for the runner"
  value       = module.iam.instance_profile_name
}

output "runner_instance_id" {
  description = "ID of the GitLab Runner EC2 instance"
  value       = module.compute.runner_instance_id
}
