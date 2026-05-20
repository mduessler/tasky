output "s3_bucket_name_dev" {
  value = module.state_bucket_dev.id
}

output "dynamodb_table_name_dev" {
  value = module.terraform_locks_dev.table_name
}

output "access_key_id_dev" {
  value = module.tasky_gitlab_runner_user_dev.access_key_id
}

output "secret_access_key_dev" {
  value     = module.tasky_gitlab_runner_user_dev.secret_access_key
  sensitive = true
}

output "user_name_dev" {
  value = module.tasky_gitlab_runner_user_dev.user_name
}
