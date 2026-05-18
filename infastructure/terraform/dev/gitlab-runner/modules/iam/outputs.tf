output "instance_profile_name" {
  description = "IAM instance profile name for the runner"
  value       = aws_iam_instance_profile.runner.name
}
