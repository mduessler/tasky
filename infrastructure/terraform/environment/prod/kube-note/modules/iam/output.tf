output "controller_profile_name" {
  value = aws_iam_instance_profile.controller.name
}

output "worker_profile_name" {
  value = aws_iam_instance_profile.worker.name
}
