output "vpc" {
  description = "ID of the VPC"
  value       = aws_vpc.this.id
}

output "vpc_cidr" {
  description = "CIDR of the vpc"
  value       = aws_vpc.this.cidr_block
}

output "private_subnet" {
  description = "ID of the private subnet"
  value       = aws_subnet.private.id
}

output "route_table_private" {
  description = "Private route table id"
  value       = aws_route_table.private.id
}
