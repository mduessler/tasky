output "compute" {
  description = "ID of EC2 instance."
  value       = aws_instance.this.id
}

output "availability_zone" {
  value = aws_instance.this.availability_zone
}
