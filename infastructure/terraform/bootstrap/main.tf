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

module "logging_dev" {
  source     = "./modules/logging"
  target_id  = module.state_bucket_dev.id
  target_arn = module.state_bucket_dev.arn
  owner_id   = var.owner_id
}

module "iam_user_dev" {
  source = "./modules/user"

  username    = "iam_user_dev"
  environment = "dev"
  project_name = var.project_name
  policies = [
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
  ]
}
