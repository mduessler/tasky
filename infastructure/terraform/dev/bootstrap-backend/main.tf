resource "aws_s3_bucket" "terraform_state" {
  bucket = "gitlab-runner-terraform-state-REDACTED_AWS_ACCOUNT"
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}
