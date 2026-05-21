module "state_bucket_dev" {
  source         = "./modules/s3_bucket"
  name           = "tasky-terraform-state-${var.owner_id}-dev"
  version_status = "Enabled"
}

module "security_dev" {
  source    = "./modules/security"
  bucket_id = module.state_bucket_dev.id
}

module "terraform_locks_dev" {
  source      = "./modules/dynamo_db"
  environment = "dev"
}

module "bucket_policy_dev" {
  source     = "./modules/s3_bucket_policy"
  bucket_id  = module.state_bucket_dev.id
  depends_on = [module.security_dev]
  policy_statements = [{
    Sid       = "DenyNonTLS"
    Effect    = "Deny"
    Principal = "*"
    Action    = "s3:*"
    Resource = [
      module.state_bucket_dev.arn,
      "${module.state_bucket_dev.arn}/*"
    ]
    Condition = {
      Bool = { "aws:SecureTransport" = "false" }
    }
  }]
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
