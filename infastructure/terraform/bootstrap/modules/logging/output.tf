output "id" {
  description = "Name of the S3 bucket logs"
  value       = aws_s3_bucket.logs.bucket
}
