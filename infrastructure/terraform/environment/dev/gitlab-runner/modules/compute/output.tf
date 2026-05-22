output "runner" {
  description = "ID of the GitLab Runner EC2 instance."
  value       = aws_instance.runner.id
}
