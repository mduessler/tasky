output "kubes" {
  description = "Set of all kubes grouped by there vpc id"
  value = {
    for kube in module.kubes : vpc_id => { conroller = kube.controller, workers = kube.workers }
  }
}
