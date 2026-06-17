output "instance_profile" {
  description = "Name of the instance profile attached to the runner."
  value       = aws_iam_instance_profile.runner.name
}
