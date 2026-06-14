data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "tasky-tf-state-${var.owner_id}-${var.environment}"
    key    = "network/terraform.tfstate"
    region = var.aws_region
  }
}

data "terraform_remote_state" "ssm_transfer_bucket" {
  backend = "s3"
  config = {
    bucket = "tasky-tf-state-${var.owner_id}-${var.environment}"
    key    = "ssm-transfer/terraform.tfstate"
    region = var.aws_region
  }
}

resource "aws_security_group" "runner" {
  name        = "runner-sg-${var.runner_name}-${var.environment}"
  description = "Security Group for GitLab Runner - outbound only"
  vpc_id      = data.terraform_remote_state.network.outputs.ids[var.availability_zone]

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

module "security" {
  source         = "./modules/security"
  environment    = var.environment
  runner_name    = var.runner_name
  ssm_bucket_arn = data.terraform_remote_state.ssm_transfer_bucket.outputs.arn
}

module "compute" {
  source               = "../../../modules/compute"
  ami_owners           = ["self"]
  ami_filter_values    = ["gitlab-runner-*"]
  instance_type        = var.instance_type
  subnet_id            = data.terraform_remote_state.network.outputs.private_subnets[var.availability_zone]
  security_groups      = [aws_security_group.runner.id]
  iam_instance_profile = module.security.iam_instance_profile
  http_hops            = 2
  root_volume_size     = 20
  tags = {
    Name = "instance-${var.environment}-${var.runner_name}"
    RunnerName = var.runner_name
  }
}
