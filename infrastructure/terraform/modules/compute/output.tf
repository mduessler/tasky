output "id" {
  description = "ID of the instance."
  value       = aws_instance.this.id
}

output "availability_zone" {
  description = "Availability zone where the instance is deployed."
  value       = aws_instance.this.availability_zone
}
