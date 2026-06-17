output "ids" {
  description = "IDs of the created block volumes."
  value       = [for volume in aws_ebs_volume.volume : volume.id]
}
