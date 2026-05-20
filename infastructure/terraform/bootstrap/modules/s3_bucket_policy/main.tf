resource "aws_s3_bucket_policy" "this" {
  bucket = var.bucket_id
  depends_on = var.depends_on
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = var.policy_statements
  })
}
