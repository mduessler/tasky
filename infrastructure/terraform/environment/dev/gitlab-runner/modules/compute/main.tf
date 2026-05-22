data "aws_ami" "gitlab_runner" {
  most_recent = true
  owners      = ["self"]

  filter {
    name   = "name"
    values = ["gitlab-runner"]
  }
}

resource "aws_instance" "runner" {
  ami                    = data.aws_ami.gitlab_runner.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.runner_security_group]
  iam_instance_profile   = var.permission_profile

  metadata_options {
    http_tokens                 = "required"
    http_endpoint               = "enabled"
    http_put_response_hop_limit = 2
  }

  root_block_device {
    encrypted   = true
    volume_type = "gp3"
    volume_size = 20
  }

  tags = {
    Name       = "runner-${var.environment}-${var.runner_name}"
    RunnerName = var.runner_name
  }
}
