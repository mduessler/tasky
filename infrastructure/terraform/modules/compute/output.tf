output "compute" {
  description = "ID of EC2 instance."
  value       = aws_instance.this.id
}
