output "id" {
  description = "ID of the storage bucket."
  value       = aws_s3_bucket.this.bucket
}

output "arn" {
  description = "ARN of the storage bucket."
  value       = aws_s3_bucket.this.arn
}
