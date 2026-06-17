output "controller_profile_name" {
  description = "Name of the instance profile attached to the controller."
  value       = aws_iam_instance_profile.controller.name
}

output "worker_profile_name" {
  description = "Name of the instance profile attached to the workers."
  value       = aws_iam_instance_profile.worker.name
}
