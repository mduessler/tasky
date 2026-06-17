data "aws_ami" "this" {
  most_recent = true
  owners      = var.image_owner

  filter {
    name   = "name"
    values = var.image_filter_values
  }
}

resource "aws_instance" "this" {
  ami                    = data.aws_ami.this.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = var.security_group_ids
  iam_instance_profile   = var.instance_profile

  metadata_options {
    http_tokens                 = "required"
    http_endpoint               = "enabled"
    http_put_response_hop_limit = var.metadata_hop_limit
  }

  root_block_device {
    encrypted   = true
    volume_type = "gp3"
    volume_size = var.root_volume_size
  }

  tags = var.tags
}
