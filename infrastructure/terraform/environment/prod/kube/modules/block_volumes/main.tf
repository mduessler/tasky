resource "aws_ebs_volume" "volume" {
  count             = length(var.sizes)
  availability_zone = var.availability_zone
  size              = var.sizes[count.index]
  type              = "gp3"
  tags = {
    Name = "${var.prefix}-${var.names[count.index]}"
  }
}
