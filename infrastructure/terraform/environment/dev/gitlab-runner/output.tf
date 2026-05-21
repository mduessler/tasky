output "gitlab_runner_instance_id" {
  description = "Instance ID des GitLab Runners (für SSM)"
  value       = module.compute.gitlab_runner
}

output "ssm_bucket_name" {
  value = module.ssm_transfer_bucket.id
}

output "ssm_session_command" {
  description = "Instruction how to connect via SSM."
  value       = "aws ssm start-session --target ${module.compute.gitlab_runner} --region ${var.aws_region} --profile tasky-dev"
}
