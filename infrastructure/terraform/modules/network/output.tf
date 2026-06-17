output "id" {
  description = "ID of the VPC."
  value       = aws_vpc.this.id
}

output "vpc_cidr" {
  description = "IP range for the VPC in CIDR notation."
  value       = aws_vpc.this.cidr_block
}

output "private_subnet" {
  description = "ID of the private subnet."
  value       = aws_subnet.private.id
}

output "route_table_private" {
  description = "ID of the private route table."
  value       = aws_route_table.private.id
}

output "public_subnet" {
  description = "ID of the public subnet."
  value       = aws_subnet.public.id
}
