data "aws_caller_identity" "current" {}

module "log_bucket" {
  source = "../../../modules/s3_bucket"
  name   = "tasky-tf-state-logs-${var.account_id}-${var.environment}"
  tags = {
    Component   = "tf-state"
    Environment = var.environment
  }

}

resource "aws_s3_bucket_ownership_controls" "logs" {
  bucket = module.log_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_logging" "source" {
  bucket        = var.target_id
  target_bucket = module.log_bucket.id
  target_prefix = "logs/"
}

data "aws_iam_policy_document" "log_bucket" {
  statement {
    sid       = "AllowS3LogDelivery"
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${module.log_bucket.arn}/logs/*"]

    principals {
      type        = "Service"
      identifiers = ["logging.s3.amazonaws.com"]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = [var.target_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }

  statement {
    sid     = "DenyNonTLS"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      module.log_bucket.arn,
      "${module.log_bucket.arn}/*",
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

resource "aws_s3_bucket_policy" "logs" {
  bucket     = module.log_bucket.id
  policy     = data.aws_iam_policy_document.log_bucket.json
  depends_on = [module.log_bucket]
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = module.log_bucket.id

  rule {
    id     = "expire-old-access-logs"
    status = "Enabled"

    filter {}

    expiration {
      days = 90
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}
