module "state_bucket_dev" {
  source         = "./modules/s3_bucket"
  name           = "tasky-terraform-state-${var.owner_id}-dev"
  version_status = "Enabled"
}

module "security" {
  source    = "./modules/security"
  bucket_id = module.state_bucket_dev.id
}

module "terraform_locks" {
  source      = "./modules/dynamodb"
  environment = "dev"
}

module "bucket_policy" {
  source = "./modules/s3_bucket_policy"
  bucket     = module.state_bucket_dev.id
  depends_on = [module.security]
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
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
  })
}

module "logging" {
  source     = "./modules/logging"
  target_id  = module.state_bucket_dev.id
  target_arn = module.state_bucket_dev.arn
  owner_id   = var.owner_id
}

module "tasky-gitlab-runner-user" {
  source = "./modules/user"

  username    = "tasky-gitlab-runner-user"
  environment = "dev"
  policies = [
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
  ]
}
