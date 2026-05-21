resource "aws_s3_bucket" "this" {
  bucket = var.name
  tags = var.tags

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "this_versioning" {
  count = var.version_status != null ? 1 : 0

  bucket = aws_s3_bucket.this.id

  versioning_configuration {
    status = var.version_status
  }
}
