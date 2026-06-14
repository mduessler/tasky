output "runner_instance_id" {
  description = "Instance ID des GitLab Runners (für SSM)."
  value       = module.compute.id
}
