output "ids" {
  description = "Id of the data-base volume"
  value       = [for id in aws_ebs_volume.postgres.ids : id]
}
