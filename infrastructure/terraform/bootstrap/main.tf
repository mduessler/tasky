module "tf_state_dev" {
  source         = "../modules/s3_bucket"
  name           = "tasky-terraform-state-${var.owner_id}-dev"
  version_status = "Enabled"
  tags = {
    Component = "terraform-state"
  }
}

data "aws_iam_policy_document" "tf_state_dev" {
  statement {
    sid     = "DenyNonTLS"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      module.tf_state_dev.arn,
      "${module.tf_state_dev.arn}/*",
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
  bucket     = module.tf_state_dev.id
  policy     = data.aws_iam_policy_document.tf_state_dev.json
  depends_on = [module.security_dev]
}

resource "aws_s3_bucket_lifecycle_configuration" "state_dev" {
  bucket = module.tf_state_dev.id

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
  target_id  = module.tf_state_dev.id
  target_arn = module.tf_state_dev.arn
  owner_id   = var.owner_id
}
