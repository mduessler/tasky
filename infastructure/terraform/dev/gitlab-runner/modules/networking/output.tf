output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "ID of the private subnet"
  value       = aws_subnet.private.id
}

output "runner_security_group_id" {
  description = "ID of the runner security group"
  value       = aws_security_group.runner.id
}
