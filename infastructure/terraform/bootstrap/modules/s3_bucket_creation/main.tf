resource "aws_s3_bucket" "this" {
  bucket = var.name

  lifecycle {
    prevent_destroy = var.destroy
  }
}

resource "aws_s3_bucket_versioning" "this_versioning" {
  bucket = aws_s3_bucket.this.id

  versioning_configuration {
    status = var.version_status
  }
}
