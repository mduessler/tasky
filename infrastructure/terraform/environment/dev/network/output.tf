output "vpc_ids" {
  value = { for az, net in module.network : az => net.vpc_id }
}
