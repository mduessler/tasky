output "s3_bucket_name" {
  value = module.state_bucket.id
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.terraform_locks.name
}

output "access_key_id" {
  value = aws_iam_access_key.this.id
}

output "secret_access_key" {
  value     = aws_iam_access_key.this.secret
  sensitive = true
}

output "user_name" {
  value = aws_iam_user.this.name
}
