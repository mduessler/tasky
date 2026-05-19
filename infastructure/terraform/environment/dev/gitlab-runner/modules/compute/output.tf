output "gitlab_runner" {
  description = "ID of the GitLab Runner EC2 instance"
  value       = aws_instance.gitlab_runner.id
