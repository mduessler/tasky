output "arn" {
  description = "Arn of the created ssm-transfer bucket"
  value = module.ssm_transfer.arn
}

output "command" {
  description = "Instruction how to connect via SSM."
  value       = "aws ssm start-session --target <Compute-ID> --region <VPC-Region> --profile <Profile-Name>"
}
