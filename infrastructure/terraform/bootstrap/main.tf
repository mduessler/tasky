module "state_bucket_dev" {
  source         = "../modules/s3_bucket"
  name           = "tasky-terraform-state-${var.owner_id}-dev"
  version_status = "Enabled"
  tags = {
    Component = "terraform-state"
  }
}

module "security_dev" {
  source    = "../modules/s3_security"
  bucket_id = module.state_bucket_dev.id
}

module "terraform_locks_dev" {
  source      = "./modules/dynamo_db"
  environment = "dev"
  tags = {
    Component = "terraform-lock-table"
  }
}

data "aws_iam_policy_document" "state_bucket_dev" {
  statement {
    sid     = "DenyNonTLS"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      module.state_bucket_dev.arn,
      "${module.state_bucket_dev.arn}/*",
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

resource "aws_s3_bucket_policy" "state_dev" {
  bucket     = module.state_bucket_dev.id
  policy     = data.aws_iam_policy_document.state_bucket_dev.json
  depends_on = [module.security_dev]
}

resource "aws_s3_bucket_lifecycle_configuration" "state_dev" {
  bucket = module.state_bucket_dev.id

  rule {
    id     = "expire-noncurrent-state-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

module "logging_dev" {
  source     = "./modules/logging"
  target_id  = module.state_bucket_dev.id
  target_arn = module.state_bucket_dev.arn
  owner_id   = var.owner_id
}
