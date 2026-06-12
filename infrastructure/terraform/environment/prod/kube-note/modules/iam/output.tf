output "controller_instance_profile" {
  value = aws_iam_instance_profile.controller.name
}

output "worker_instance_profile" {
  value = aws_iam_instance_profile.worker.name
}
