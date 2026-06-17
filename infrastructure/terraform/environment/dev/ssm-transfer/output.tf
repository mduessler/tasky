output "arn" {
  description = "ARN of the SSM transfer bucket."
  value       = module.ssm_transfer.arn
}

output "command" {
  description = "Command to start an SSM session to the instance."
  value       = "aws ssm start-session --target <Compute-ID> --region <VPC-Region> --profile <Profile-Name>"
}
