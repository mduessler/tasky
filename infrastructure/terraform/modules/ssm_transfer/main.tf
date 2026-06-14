module "s3" {
  source = "../s3_bucket"
  name   = "ssm-transfer-${var.owner_id}-${var.environment}"
  tags = {
    Component   = "ssm-transfer-bucket"
    Environment = var.environment
  }
}

data "aws_iam_policy_document" "ssm_bucket" {
  statement {
    sid     = "DenyNonTLS"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      module.s3.arn,
      "${module.s3.arn}/*",
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
  bucket     = module.s3.id
  policy     = data.aws_iam_policy_document.ssm_bucket.json
  depends_on = [module.s3]
}

resource "aws_s3_bucket_lifecycle_configuration" "ssm_bucket" {
  bucket = module.s3.id

  rule {
    id     = "delete-stale-ssm-transfer-objects"
    status = "Enabled"
    filter {}

    expiration {
      days = 1
    }
  }
}
