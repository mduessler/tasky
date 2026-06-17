output "kubes" {
  description = "Set of all kubes grouped by their vpc id"
  value = {
    for kube in module.kubes : kube.vpc_id => { controller = kube.controller, workers = kube.workers }
  }
}

output "db_volumes" {
  description = "Set of all db volumes grouped by availability zone"
  value       = { for az, ebs in module.db_volumes : az => ebs.ids }

}
