resource "aws_iam_user" "this" {
  name = var.username

  tags = {
    Environment = var.environment
    Project     = "tasky"
    ManagedBy   = "terraform"
  }

}

resource "aws_iam_access_key" "this" {
  user = aws_iam_user.this.name
}

resource "aws_iam_user_policy_attachment" "this" {
  for_each   = toset(var.policies)
  user       = aws_iam_user.this.name
  policy_arn = each.value
}
