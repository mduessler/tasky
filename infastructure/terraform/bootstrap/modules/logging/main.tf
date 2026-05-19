data "aws_caller_identity" "current" {}

module "s3_bucket" {
  source          = "../s3_bucket"
  name            = "gitlab-runner-terraform-state-logs-${var.owner_id}"
  prevent_destroy = true
  version_status  = "Enabled"
}

module "security" {
  source    = "../security"
  bucket_id = module.s3_bucket.id
}

resource "aws_s3_bucket_ownership_controls" "logs" {
  bucket = module.s3_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_logging" "source" {
  bucket        = var.target_id
  target_bucket = module.s3_bucket.id
  target_prefix = "logs/"
}

resource "aws_s3_bucket_policy" "logs" {
  bucket = module.s3_bucket.id

  depends_on = [module.security]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowS3LogDelivery"
        Effect = "Allow"
        Principal = {
          Service = "logging.s3.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${module.s3_bucket.arn}/logs/*"
        Condition = {
          ArnLike = {
            "aws:SourceArn" = var.target_arn
          }
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      },
      {
        Sid       = "DenyNonTLS"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          module.s3_bucket.arn,
          "${module.s3_bucket.arn}/*"
        ]
        Condition = {
          Bool = { "aws:SecureTransport" = "false" }
        }
      }
    ]
  })
}
