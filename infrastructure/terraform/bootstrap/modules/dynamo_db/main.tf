resource "aws_dynamodb_table" "this" {
  name         = "tasky-terraform-locks-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  tags = var.tags

  attribute {
    name = "LockID"
    type = "S"
  }
}
