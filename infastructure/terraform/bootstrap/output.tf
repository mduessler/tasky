output "s3_bucket_name" {
  value = module.s3_bucket.id
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.terraform_locks.name
}
