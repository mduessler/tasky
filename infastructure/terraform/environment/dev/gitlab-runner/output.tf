output "gitlab_runner_instance_id" {
  description = "Instance ID des GitLab Runners (für SSM)"
  value       = module.compute.gitlab_runner
}
