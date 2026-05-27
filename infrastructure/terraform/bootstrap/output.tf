output "s3_bucket_name_dev" {
  value = module.state_bucket_dev.id
}

output "dynamodb_table_name_dev" {
  value = module.terraform_locks_dev.table_name
}
