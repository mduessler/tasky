output "kubes" {
  description = "Set of all kubes grouped by their VPC ID."
  value = {
    for kube in module.kubes : kube.vpc_id => { controller_endpoint = kube.controller_endpoint, workers = kube.workers }
  }
}

output "postgres_volumes" {
  description = "Set of all PostgreSQL volumes grouped by availability zone."
  value       = { for az, ebs in module.postgres_volumes : az => ebs.ids }
}

output "etcd_volumes" {
  description = "Set of all etcd volumes grouped by availability zone."
  value       = { for az, ebs in module.etcd_volumes : az => ebs.ids }
}
