output "arn" {
  description = "ARN of the ssm-transfer bucket."
  value       = module.s3.arn
}
