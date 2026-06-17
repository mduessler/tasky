output "kubes" {
  description = "Set of all kubes grouped by their VPC ID."
  value = {
    for kube in module.kubes : kube.vpc_id => { controller = kube.controller, workers = kube.workers }
  }
}

output "db_volumes" {
  description = "Set of all database volumes grouped by availability zone."
  value       = { for az, ebs in module.db_volumes : az => ebs.ids }
}
