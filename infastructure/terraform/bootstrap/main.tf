module "state_bucket" {
  source          = "./modules/s3_bucket"
  name            = "tasky-gitlab-runner-terraform-state-${var.owner_id}"
  version_status = "Enabled"
}

module "security" {
  source    = "./modules/security"
  bucket_id = module.state_bucket.id
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "tasky-gitlab-runner-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

resource "aws_s3_bucket_policy" "terraform_state" {
  bucket = module.state_bucket.id

  depends_on = [module.security]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyNonTLS"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource = [
        module.state_bucket.arn,
        "${module.state_bucket.arn}/*"
      ]
      Condition = {
        Bool = { "aws:SecureTransport" = "false" }
      }
    }]
  })
}

module "logging" {
  source     = "./modules/logging"
  target_id  = module.state_bucket.id
  target_arn = module.state_bucket.arn
  owner_id = var.owner_id
}
