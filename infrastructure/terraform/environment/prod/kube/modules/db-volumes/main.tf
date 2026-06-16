resource "aws_ebs_volume" "postgres" {
  availability_zone = var.availability_zone
  size              = var.size
  type              = "gp3"
  tags = {
    Name = "postgres-data-${var.name}"
  }
}
