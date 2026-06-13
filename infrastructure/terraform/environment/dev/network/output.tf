output "vpc_ids" {
  description = "List of all created vpcs for the development"
  value       = { for az, net in module.network : az => net.vpc }
}
