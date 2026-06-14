data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "tasky-tf-state-${var.owner_id}-${var.environment}"
    key    = "network/terraform.tfstate"
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
  ssm_bucket_arn = module.ssm_transfer_bucket.arn
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
  }
}

module "ssm_transfer_bucket" {
  source = "../../../modules/s3_bucket"
  name   = "ansible-ssm-${var.owner_id}-${var.environment}"
  tags = {
    Component = "ansible-ssm-transfer"
  }
}

data "aws_iam_policy_document" "ssm_bucket" {
  statement {
    sid     = "DenyNonTLS"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      module.ssm_transfer_bucket.arn,
      "${module.ssm_transfer_bucket.arn}/*",
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "ssm_bucket" {
  bucket     = module.ssm_transfer_bucket.id
  policy     = data.aws_iam_policy_document.ssm_bucket.json
  depends_on = [module.ssm_transfer_bucket]
}

resource "aws_s3_bucket_lifecycle_configuration" "ssm_bucket" {
  bucket = module.ssm_transfer_bucket.id

  rule {
    id     = "delete-stale-ansible-objects"
    status = "Enabled"
    filter {}

    expiration {
      days = 1
    }
  }
}
