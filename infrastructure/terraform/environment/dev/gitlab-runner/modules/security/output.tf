output "instance_profile_name" {
  description = "Permission/IAM instance profile name for the runner."
  value       = aws_iam_instance_profile.runner.name
}
