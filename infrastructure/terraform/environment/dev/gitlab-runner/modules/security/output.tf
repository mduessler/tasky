output "iam_instance_profile" {
  description = "Permission/IAM instance profile name for the runner."
  value       = aws_iam_instance_profile.runner.name
}
