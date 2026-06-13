module "tf_state" {
  source         = "../../../modules/s3_bucket"
  name           = "tasky-tf-state-${var.owner_id}-${var.environment}"
  version_status = "Enabled"
  tags = {
    Component   = "tf-state"
    Environment = var.environment
  }
}

data "aws_iam_policy_document" "tf_state" {
  statement {
    sid     = "DenyNonTLS"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      module.tf_state.arn,
      "${module.tf_state.arn}/*",
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

resource "aws_s3_bucket_policy" "state" {
  bucket     = module.tf_state.id
  policy     = data.aws_iam_policy_document.tf_state.json
  depends_on = [module.tf_state]
}

resource "aws_s3_bucket_lifecycle_configuration" "state" {
  bucket = module.tf_state.id

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

module "logging" {
  source      = "../logging"
  target_id   = module.tf_state.id
  target_arn  = module.tf_state.arn
  environment = var.environment
  owner_id    = var.owner_id
}
