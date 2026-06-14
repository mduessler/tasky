output "id" {
  value = module.ssm_transfer.id
}

output "command" {
  description = "Instruction how to connect via SSM."
  value       = "aws ssm start-session --target <Compute-ID> --region <VPC-Region> --profile <Profile-Name>"
}
