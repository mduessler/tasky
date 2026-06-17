output "endpoint" {
  description = "DNS name of the internal load balancer for the controller API server."
  value       = aws_lb.this.dns_name
}
