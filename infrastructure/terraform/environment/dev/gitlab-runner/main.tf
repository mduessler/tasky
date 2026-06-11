module "network" {
  source             = "../../../modules/network"
  aws_region  = var.aws_region
}

resource "aws_security_group" "runner" {
  name        = "runner-sg-${var.runner_name}"
  description = "Security Group for GitLab Runner - outbound only"
  vpc_id      = network.vpc.id

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
  source             = "../../../modules/compute"
  ami_owners         = ["self"]
  ami_filter_values  = ["gitlab-runner-*"]
  instance_type      = var.instance_type
  subnet_id          = module.network.private_subnet
  security_groups    = [aws_security_group.runner.id]
  permission_profile = module.security.instance_profile_name
  http_hops          = 2
  root_volume_size   = 20
  namespace          = var.environment
  name               = var.runner_name
}

module "ssm_transfer_bucket" {
  source = "../../../modules/s3_bucket"
  name   = "ansible-ssm-${var.owner_id}-${var.environment}"
  tags = {
    Component = "ansible-ssm-transfer"
  }
}

module "ssm_bucket_security" {
  source    = "../../../modules/s3_security"
  bucket_id = module.ssm_transfer_bucket.id
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
  depends_on = [module.ssm_bucket_security]
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
