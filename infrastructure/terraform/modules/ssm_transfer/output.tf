output "arn" {
  description = "ARN of the SSM transfer bucket."
  value       = module.s3.arn
}
