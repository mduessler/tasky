output "ids" {
  description = "Id of the data-base volume"
  value       = [for volume in aws_ebs_volume.volume : volume.id]
}
