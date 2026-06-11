data "aws_ami" "this" {
  most_recent = true
  owners      = var.ami_owners

  filter {
    name   = "name"
    values = var.ami_filter_values
  }
}

resource "aws_instance" "this" {
  ami                    = data.aws_ami.this.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = var.security_groups
  iam_instance_profile   = var.permission_profile

  metadata_options {
    http_tokens                 = "required"
    http_endpoint               = "enabled"
    http_put_response_hop_limit = var.http_hops
  }

  root_block_device {
    encrypted   = true
    volume_type = "gp3"
    volume_size = var.root_volume_size
  }

  tags = {
    Name = "instance-${var.namespace}-${var.name}"
  }
}
